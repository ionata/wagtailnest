from pkg_resources import get_distribution


__version__ = get_distribution('wagtailnest').version
default_app_config = 'wagtailnest.apps.WagtailnestConfig'
