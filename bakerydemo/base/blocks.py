from wagtail.images.blocks import ImageChooserBlock
from wagtail.embeds.blocks import EmbedBlock
from wagtail.core.blocks import (
    CharBlock, ChoiceBlock, RichTextBlock, StreamBlock, StructBlock, TextBlock,
)
from wagtailcodeblock.blocks import CodeBlock

from django.utils.safestring import mark_safe

from pygments import highlight
from pygments.formatters import get_formatter_by_name
from pygments.lexers import get_lexer_by_name

from django.conf import settings


class ImageBlock(StructBlock):
    """
    Custom `StructBlock` for utilizing images with associated caption and
    attribution data
    """
    image = ImageChooserBlock(required=True)
    caption = CharBlock(required=False)
    attribution = CharBlock(required=False)

    class Meta:
        icon = 'image'
        template = "blocks/image_block.html"


class HeadingBlock(StructBlock):
    """
    Custom `StructBlock` that allows the user to select h2 - h4 sizes for headers
    """
    heading_text = CharBlock(classname="title", required=True)
    size = ChoiceBlock(choices=[
        ('', 'Select a header size'),
        ('h2', 'H2'),
        ('h3', 'H3'),
        ('h4', 'H4')
    ], blank=True, required=False)

    class Meta:
        icon = "title"
        template = "blocks/heading_block.html"


class BlockQuote(StructBlock):
    """
    Custom `StructBlock` that allows the user to attribute a quote to the author
    """
    text = TextBlock()
    attribute_name = CharBlock(
        blank=True, required=False, label='e.g. Mary Berry')

    class Meta:
        icon = "fa-quote-left"
        template = "blocks/blockquote.html"

class JupyterCode(StructBlock):

    def __init__(self, local_blocks=None, **kwargs):
        # Languages included in PrismJS core
        # Review: https://github.com/PrismJS/prism/blob/gh-pages/prism.js#L602
        self.INCLUDED_LANGUAGES = (
            ('html', 'HTML'),
            ('mathml', 'MathML'),
            ('svg', 'SVG'),
            ('xml', 'XML'),
        )

        if local_blocks is None:
            local_blocks = []
        else:
            local_blocks = local_blocks.copy()

        language_choices, language_default = self.get_language_choice_list(**kwargs)

        local_blocks.extend([
            ('language', ChoiceBlock(
                choices=language_choices,
                default=language_default,
                identifier='language',
            )),
            ('code', TextBlock(label='Code', identifier='code')),
        ])

        super().__init__(local_blocks, **kwargs)

    def get_language_choices(self):
        """
        Default list of language choices, if not overridden by Django.
        """
        DEFAULT_LANGUAGES = (
            ('python', 'Python'),
            ('scss', 'SCSS'),
            ('yaml', 'YAML'),
        )

        return getattr(settings, "WAGTAIL_CODE_BLOCK_LANGUAGES", DEFAULT_LANGUAGES)

    def get_language_choice_list(self, **kwargs):
        # Get default languages
        WCB_LANGUAGES = self.get_language_choices()
        # If a language is passed in as part of a code block, use it.
        language = kwargs.get('language', False)

        total_language_choices = WCB_LANGUAGES + self.INCLUDED_LANGUAGES

        if language in [lang[0] for lang in total_language_choices]:
            for language_choice in total_language_choices:
                if language_choice[0] == language:
                    language_choices = (language_choice,)
                    language_default = language_choice[0]
        else:
            language_choices = WCB_LANGUAGES
            language_default = None

        return language_choices, language_default

    def get_theme(self):
        """
        Returns a default theme, if not in the proejct's settings. Default theme is 'coy'.
        """

        return getattr(settings, "WAGTAIL_CODE_BLOCK_THEME", 'coy')

    def get_prism_version(self):
        prism_version = "1.17.1"

        return prism_version

    class Meta:
        icon = 'code'
        template = 'blocks/jupytercode_block.html'
        form_classname = 'code-block struct-block'
        form_template = 'blocks/jupytercode_block_form.html'


# StreamBlocks
class BaseStreamBlock(StreamBlock):
    """
    Define the custom blocks that `StreamField` will utilize
    """
    heading_block = HeadingBlock()
    paragraph_block = RichTextBlock(
        icon="fa-paragraph",
        template="blocks/paragraph_block.html"
    )
    image_block = ImageBlock()
    block_quote = BlockQuote()
    embed_block = EmbedBlock(
        help_text='Insert an embed URL e.g https://www.youtube.com/embed/SGJFWirQ3ks',
        icon="fa-s15",
        template="blocks/embed_block.html")
    """""code_block = CodeBlock(label='Code')"""
    jupyter_block = JupyterCode(label='Code')



