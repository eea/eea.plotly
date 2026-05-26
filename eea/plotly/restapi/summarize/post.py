"""REST API endpoint to trigger LLM summary generation for visualizations"""

import logging
import uuid

import transaction
from plone import api
from plone.restapi.services import Service

from eea.genai.summary.subscribers import generate_summary_for
from eea.plotly.interfaces import IPlotlyLayer

logger = logging.getLogger("eea.plotly")

COMMIT_BATCH_SIZE = 100


class VisualizationsSummarize(Service):
    """Trigger LLM summary generation for visualizations with empty llm_summary."""

    def reply(self):
        if not IPlotlyLayer.providedBy(self.request):
            return {
                "status": "error",
                "message": "This endpoint is only available on Plotly-enabled sites",
            }

        path = self._get_path()
        visualizations = self._get_visualizations_with_empty_summary(path)

        if not visualizations:
            return {
                "status": "success",
                "message": "No visualizations with empty llm_summary found",
                "path": path,
                "count": 0,
            }

        job_id = str(uuid.uuid4())
        result = self._process_visualizations(visualizations, job_id)

        return {
            "status": "success",
            "job_id": job_id,
            "path": path,
            "total": len(visualizations),
            "processed": result["processed"],
            "skipped_locked": result["skipped_locked"],
            "errors": result["errors"],
        }

    def _get_path(self):
        context = self.context
        if context is not None:
            return "/".join(context.getPhysicalPath())
        return "/"

    def _get_visualizations_with_empty_summary(self, path):
        portal = api.portal.get()
        site_path = "/".join(portal.getPhysicalPath())
        search_path = path if path.startswith(site_path) else site_path

        catalog = api.portal.get_tool("portal_catalog")
        results = catalog.searchResults(
            portal_type="visualization",
            path=search_path,
            sort_on="path",
        )

        visualizations = []
        for brain in results:
            try:
                obj = brain.getObject()
                if obj is None:
                    continue
                llm_summary = getattr(obj, "llm_summary", None)
                if not llm_summary or not llm_summary.strip():
                    visualizations.append(obj)
            except Exception as exc:
                logger.warning(f"Could not access {brain.getURL()}: {exc}")
                continue

        return visualizations

    def _check_locked(self, obj):
        try:
            from plone.locking.interfaces import ILockable

            if ILockable.providedBy(obj):
                return ILockable(obj).locked()
        except ImportError:
            pass

        try:
            return getattr(obj, "locked", False)
        except Exception:
            return False

    def _process_visualizations(self, visualizations, job_id):
        processed = 0
        skipped_locked = 0
        errors = []
        pending = 0

        for obj in visualizations:
            url = obj.absolute_url()
            try:
                if self._check_locked(obj):
                    logger.info(f"[{job_id}] Skipping locked visualization: {url}")
                    skipped_locked += 1
                    continue

                generate_summary_for(obj, self.request)
                processed += 1
                pending += 1
                logger.info(f"[{job_id}] Updated llm_summary for {url}")

                if pending >= COMMIT_BATCH_SIZE:
                    transaction.commit()
                    logger.info(f"[{job_id}] Committed batch of {pending}")
                    pending = 0

            except Exception as exc:
                msg = f"{url}: {exc}"
                logger.error(f"[{job_id}] Error processing {msg}")
                errors.append(msg)
                continue

        if pending > 0:
            transaction.commit()
            logger.info(f"[{job_id}] Committed final batch of {pending}")

        logger.info(
            f"[{job_id}] Completed: processed={processed}, "
            f"skipped_locked={skipped_locked}, errors={len(errors)}"
        )

        return {
            "processed": processed,
            "skipped_locked": skipped_locked,
            "errors": errors,
        }
