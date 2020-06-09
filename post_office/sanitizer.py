from django.utils.html import mark_safe, strip_tags
from django.utils.text import format_lazy
from django.utils.translation import gettext_lazy

try:
    import bleach

    clean_html = lambda body: mark_safe(bleach.clean(
        body,
        tags=[
            'a',
            'abbr',
            'acronym',
            'b',
            'blockquote',
            'br',
            'caption',
            'center',
            'code',
            'em',
            'div',
            'font',
            'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
            'head',
            'hr',
            'i',
            'img',
            'label',
            'li',
            'ol',
            'p',
            'pre',
            'span',
            'strong',
            'table', 'tbody', 'tfoot', 'td', 'th', 'thead', 'tr',
            'u',
            'ul',
        ],
        attributes={
            'a': ['class', 'href', 'id', 'style', 'target'],
            'abbr': ['class', 'id', 'style'],
            'acronym': ['class', 'id', 'style'],
            'b': ['class', 'id', 'style'],
            'blockquote': ['class', 'id', 'style'],
            'br': ['class', 'id', 'style'],
            'caption': ['class', 'id', 'style'],
            'center': ['class', 'id', 'style'],
            'code': ['class', 'id', 'style'],
            'em': ['class', 'id', 'style'],
            'div': ['class', 'id', 'style', 'align', 'dir'],
            'font': ['class', 'id', 'style', 'color', 'face', 'size'],
            'h1': ['class', 'id', 'style', 'align', 'dir'],
            'h2': ['class', 'id', 'style', 'align', 'dir'],
            'h3': ['class', 'id', 'style', 'align', 'dir'],
            'h4': ['class', 'id', 'style', 'align', 'dir'],
            'h5': ['class', 'id', 'style', 'align', 'dir'],
            'h6': ['class', 'id', 'style', 'align', 'dir'],
            'head': ['dir', 'lang'],
            'hr': ['align', 'size', 'width'],
            'i': ['class', 'id', 'style'],
            'img': ['class', 'id', 'style', 'align', 'border', 'height', 'hspace', 'src', 'usemap', 'vspace', 'width'],
            'label': ['class', 'id', 'style'],
            'li': ['class', 'id', 'style', 'dir', 'type'],
            'ol': ['class', 'id', 'style', 'dir', 'type'],
            'p': ['class', 'id', 'style', 'align', 'dir'],
            'pre': ['class', 'id', 'style'],
            'span': ['class', 'id', 'style'],
            'strong': ['class', 'id', 'style'],
            'table': ['class', 'id', 'style', 'align', 'bgcolor', 'border', 'cellpadding', 'cellspacing', 'dir', 'frame', 'rules', 'width'],
            'tbody': ['class', 'id', 'style'],
            'tfoot': ['class', 'id', 'style'],
            'td': ['class', 'id', 'style', 'abbr', 'align', 'bgcolor', 'colspan', 'dir', 'height', 'lang', 'rowspan', 'scope', 'style', 'valign', 'width'],
            'th': ['class', 'id', 'style', 'abbr', 'align', 'background', 'bgcolor', 'colspan', 'dir', 'height', 'lang', 'scope', 'style', 'valign', 'width'],
            'thead': ['class', 'id', 'style'],
            'tr': ['class', 'id', 'style', 'align', 'bgcolor', 'dir', 'style', 'valign'],
            'u': ['class', 'id', 'style'],
            'ul': ['class', 'id', 'style', 'dir', 'type'],
        },
        strip=True,
        strip_comments=True,
        styles=[
            'border', 'border-top', 'border-right', 'border-bottom', 'border-left',
            'border-radius',
            'box-shadow',
            'height',
            'margin', 'margin-top', 'margin-right', 'margin-bottom', 'margin-left',
            'padding', 'padding-top', 'padding-right', 'padding-bottom', 'padding-left',
            'width',
            'max-width',
            'min-width',
            'border-collapse',
            'border-spacing',
            'caption-side',
            'empty-cells',
            'table-layout',
            'direction',
            'font',
            'font-family',
            'font-style',
            'font-variant',
            'font-size',
            'font-weight',
            'letter-spacing',
            'line-height',
            'text-align',
            'text-decoration',
            'text-indent',
            'text-overflow',
            'text-shadow',
            'text-transform',
            'white-space',
            'word-spacing',
            'word-wrap',
            'vertical-align',
            'color',
            'background',
            'background-color',
            'background-image',
            'background-position',
            'background-repeat',
            'bottom',
            'clear',
            'cursor',
            'display',
            'float',
            'left',
            'opacity',
            'outline',
            'overflow',
            'position',
            'resize',
            'right',
            'top',
            'visibility',
            'z-index',
            'list-style-position',
            'list-style-tyle',
        ],
    ))
except ImportError:
    # if bleach is not installed, handle rendered HTML as plain text
    clean_html = lambda body: mark_safe(format_lazy('<p><em>({heading})</em></p><div>{body}</div>',
                                                    heading=gettext_lazy("stripping all HTML tags"),
                                                    body=strip_tags(body)))
