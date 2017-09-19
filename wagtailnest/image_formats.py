from django.utils.html import escape
from wagtail.wagtailimages.formats import Format as BaseFormat
from wagtail.wagtailimages.shortcuts import get_rendition_or_not_found

from wagtailnest.utils import generate_image_url


class Format(BaseFormat):
    # Override to get the CMS API URL instead of a relative one
    def image_to_html(self, image, alt_text, extra_attributes=''):
        rendition = get_rendition_or_not_found(image, self.filter_spec)

        if self.classnames:
            class_attr = 'class="%s" ' % escape(self.classnames)
        else:
            class_attr = ''

        url = generate_image_url(image, self.filter_spec)

        return '<img %s%ssrc="%s" width="%d" height="%d" alt="%s">' % (
            extra_attributes, class_attr,
            escape(url), rendition.width, rendition.height, alt_text
        )

    @classmethod
    def new(cls, name, filter_spec, classnames=None, label=None):
        if label is None:
            label = name.replace('-', ' ').title()
        if classnames is None:
            classnames = 'richtext-image ' + name
        return cls(name, label, classnames, filter_spec)
