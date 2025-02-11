""" Main product initializer
"""
from zope.i18nmessageid.message import MessageFactory
#__import__('pkg_resources').declare_namespace(__name__)

EEAMessageFactory = MessageFactory('eea')


def initialize(context):
    """Initializer called when used as a Zope 2 product.
    """
