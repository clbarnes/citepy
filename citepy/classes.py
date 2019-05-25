from __future__ import annotations

import json
from datetime import date
from enum import Enum
from numbers import Number
from typing import Union, Optional, List, Any, Iterable, Dict

from citepy.validate import type_validator, name_validator, date_validator, item_validator

StrNum = Union[str, Number]
StrNumBool = Union[str, Number, bool]


class JSONDecoderError(object):
    pass


class CslObject:
    _validator = None

    def __init__(self, **kwargs):
        self._check_types()

    def to_jso(self):
        out = py_to_jso(self.__dict__)
        self._validator.validate(out)
        return out

    @classmethod
    def from_jso(cls, jso) -> CslObject:
        cls._validator.validate(jso)
        return cls(**jso_to_py(jso))

    def _check_types(self):
        self.to_jso()
        # type_hints = get_type_hints(self)
        # for attr_name, type_hint in type_hints.items():
        #     with suppress(KeyError):  # Assume un-annotated parameters can be any type
        #         value = getattr(self, attr_name)
        #         if isinstance(type_hint, _SpecialForm):
        #             # No check for typing.Any, typing.Union, typing.ClassVar (without parameters)
        #             continue
        #         try:
        #             actual_type = type_hint.__origin__
        #         except AttributeError:
        #             actual_type = type_hint
        #         if isinstance(actual_type, _SpecialForm):
        #             # case of typing.Union[…] or typing.ClassVar[…]
        #             actual_type = type_hint.__args__
        #
        #         if not isinstance(value, actual_type):
        #             raise TypeError('Unexpected type for \'{}\' (expected {} but found {})'.format(name, type_hint, type(value)))

    def __str__(self):
        return json.dumps(self.to_jso())

    def __eq__(self, other):
        if isinstance(other, str):
            try:
                other_jso = json.loads(other)
            except JSONDecoderError:
                return False
        elif isinstance(other, CslObject):
            other_jso = other.to_jso()
        else:
            other_jso = other

        return self.to_jso() == other_jso


class CslType(Enum):
    ARTICLE = "article"
    ARTICLE_JOURNAL = "article-journal"
    ARTICLE_MAGAZINE = "article-magazine"
    ARTICLE_NEWSPAPER = "article-newspaper"
    BILL = "bill"
    BOOK = "book"
    BROADCAST = "broadcast"
    CHAPTER = "chapter"
    DATASET = "dataset"
    ENTRY = "entry"
    ENTRY_DICTIONARY = "entry-dictionary"
    ENTRY_ENCYCLOPEDIA = "entry-encyclopedia"
    FIGURE = "figure"
    GRAPHIC = "graphic"
    INTERVIEW = "interview"
    LEGAL_CASE = "legal_case"
    LEGISLATION = "legislation"
    MANUSCRIPT = "manuscript"
    MAP = "map"
    MOTION_PICTURE = "motion_picture"
    MUSICAL_SCORE = "musical_score"
    PAMPHLET = "pamphlet"
    PAPER_CONFERENCE = "paper-conference"
    PATENT = "patent"
    PERSONAL_COMMUNICATION = "personal_communication"
    POST = "post"
    POST_WEBLOG = "post-weblog"
    REPORT = "report"
    REVIEW = "review"
    REVIEW_BOOK = "review-book"
    SONG = "song"
    SPEECH = "speech"
    THESIS = "thesis"
    TREATY = "treaty"
    WEBPAGE = "webpage"

    def to_jso(self):
        out = self.value
        type_validator.validate(out)
        return out

    @classmethod
    def from_jso(cls, value) -> CslType:
        type_validator.validate(value)
        return CslType(value)


class CslName(CslObject):
    _validator = name_validator

    def __init__(
        self,
        family: Optional[str] = None,
        given: Optional[str] = None,
        dropping_particle: Optional[str] = None,
        non_dropping_particle: Optional[str] = None,
        suffix: Optional[str] = None,
        comma_suffix: Optional[StrNumBool] = None,
        static_ordering: Optional[StrNumBool] = None,
        literal: Optional[str] = None,
        parse_names: Optional[StrNumBool] = None,
    ):
        self.family: Optional[str] = family
        self.given: Optional[str] = given
        self.dropping_particle: Optional[str] = dropping_particle
        self.non_dropping_particle: Optional[str] = non_dropping_particle
        self.suffix: Optional[str] = suffix
        self.comma_suffix: Optional[StrNumBool] = comma_suffix
        self.static_ordering: Optional[StrNumBool] = static_ordering
        self.literal: Optional[str] = literal
        self.parse_names: Optional[StrNumBool] = parse_names

        super().__init__()


class CslDate(CslObject):
    _validator = date_validator

    def __init__(
        self,
        date_parts: Optional[List[List[StrNum]]] = None,
        season: Optional[StrNum] = None,
        circa: Optional[StrNumBool] = None,
        literal: Optional[str] = None,
        raw: Optional[str] = None,
    ):
        # outer has <=2 items, inner has <=3
        self.date_parts: Optional[List[List[StrNum]]] = date_parts
        self.season: Optional[StrNum] = season
        self.circa: Optional[StrNumBool] = circa
        self.literal: Optional[str] = literal
        self.raw: Optional[str] = raw

        super().__init__()

    @classmethod
    def from_date(cls, start, end=None):
        lsts = [[start.year, start.month, start.day]]
        if end is not None:
            lsts.append([end.year, end.month, end.day])
        return cls(lsts)


ValidName = Union[CslName, str, Dict[str, Any]]


def normalise_name(obj: ValidName) -> CslName:
    if isinstance(obj, CslName):
        return obj
    elif isinstance(obj, str):
        return CslName(literal=obj)
    elif isinstance(obj, dict):
        return CslName.from_jso(obj)
    else:
        raise TypeError(f"Don't know how to normalise name of type {type(obj)}")


def normalise_name_list(obj: Optional[Union[ValidName, Iterable[ValidName]]]) -> Optional[List[CslName]]:
    if obj is None:
        return obj

    try:
        return [normalise_name(obj)]
    except TypeError:
        pass

    return [normalise_name(item) for item in obj]


ValidDate = Union[date, CslDate, Dict[str, Any], str, List[List[Number]]]


def normalise_date(obj: Optional[ValidDate]) -> Optional[CslDate]:
    if obj is None or isinstance(obj, CslDate):
        return obj

    if isinstance(obj, dict):
        return CslDate.from_jso(obj)

    if isinstance(obj, str):
        return CslDate(literal=obj)

    if isinstance(obj, Iterable):
        obj = list(obj)
        if all(isinstance(item, date) for item in obj):
            return CslDate.from_date(*obj)
        return CslDate(date_parts=obj)

    if isinstance(obj, date):
        return CslDate.from_date(obj)

    raise TypeError(f"Not sure how to normalise date from type {type(obj)}")


class CslItem(CslObject):
    _validator = item_validator

    def __init__(
        self,
        type: Union[str, CslType],
        id: StrNum,
        categories: Optional[List[str]] = None,
        language: Optional[str] = None,
        journal_abbreviation: Optional[str] = None,
        short_title: Optional[str] = None,
        author: Optional[List[ValidName]] = None,
        collection_editor: Optional[List[ValidName]] = None,
        composer: Optional[List[ValidName]] = None,
        container_author: Optional[List[ValidName]] = None,
        director: Optional[List[ValidName]] = None,
        editor: Optional[List[ValidName]] = None,
        editorial_director: Optional[List[ValidName]] = None,
        interviewer: Optional[List[ValidName]] = None,
        illustrator: Optional[List[ValidName]] = None,
        original_author: Optional[List[ValidName]] = None,
        recipient: Optional[List[ValidName]] = None,
        reviewed_author: Optional[List[ValidName]] = None,
        translator: Optional[List[ValidName]] = None,
        accessed: Optional[ValidDate] = None,
        container: Optional[ValidDate] = None,
        event_date: Optional[ValidDate] = None,
        issued: Optional[ValidDate] = None,
        original_date: Optional[ValidDate] = None,
        submitted: Optional[ValidDate] = None,
        abstract: Optional[str] = None,
        annote: Optional[str] = None,
        archive: Optional[str] = None,
        archive_location: Optional[str] = None,
        archive_place: Optional[str] = None,
        authority: Optional[str] = None,
        call_number: Optional[str] = None,
        chapter_number: Optional[str] = None,
        citation_number: Optional[str] = None,
        citation_label: Optional[str] = None,
        collection_number: Optional[str] = None,
        collection_title: Optional[str] = None,
        container_title: Optional[str] = None,
        container_title_short: Optional[str] = None,
        dimensions: Optional[str] = None,
        DOI: Optional[str] = None,
        edition: Optional[StrNum] = None,
        event: Optional[str] = None,
        event_place: Optional[str] = None,
        first_reference_note_number: Optional[str] = None,
        genre: Optional[str] = None,
        ISBN: Optional[str] = None,
        ISSN: Optional[str] = None,
        issue: Optional[StrNum] = None,
        jurisdiction: Optional[str] = None,
        keyword: Optional[str] = None,
        locator: Optional[str] = None,
        medium: Optional[str] = None,
        note: Optional[str] = None,
        number: Optional[StrNum] = None,
        number_of_pages: Optional[str] = None,
        number_of_volumes: Optional[StrNum] = None,
        original_publisher: Optional[str] = None,
        original_publisher_place: Optional[str] = None,
        original_title: Optional[str] = None,
        page: Optional[str] = None,
        page_first: Optional[str] = None,
        PMCID: Optional[str] = None,
        PMID: Optional[str] = None,
        publisher: Optional[str] = None,
        publisher_place: Optional[str] = None,
        references: Optional[str] = None,
        reviewed_title: Optional[str] = None,
        scale: Optional[str] = None,
        section: Optional[str] = None,
        source: Optional[str] = None,
        status: Optional[str] = None,
        title: Optional[str] = None,
        title_short: Optional[str] = None,
        URL: Optional[str] = None,
        version: Optional[str] = None,
        volume: Optional[StrNum] = None,
        year_suffix: Optional[StrNum] = None,
    ):
        self.type: CslType = CslType(type)
        self.id: StrNum = id
        self.categories: Optional[List[str]] = categories
        self.language: Optional[str] = language
        self.journal_abbreviation: Optional[str] = journal_abbreviation
        self.short_title: Optional[str] = short_title

        self.author: Optional[List[CslName]] = normalise_name_list(author)
        self.collection_editor: Optional[List[CslName]] = normalise_name_list(collection_editor)
        self.composer: Optional[List[CslName]] = normalise_name_list(composer)
        self.container_author: Optional[List[CslName]] = normalise_name_list(container_author)
        self.director: Optional[List[CslName]] = normalise_name_list(director)
        self.editor: Optional[List[CslName]] = normalise_name_list(editor)
        self.editorial_director: Optional[List[CslName]] = normalise_name_list(editorial_director)
        self.interviewer: Optional[List[CslName]] = normalise_name_list(interviewer)
        self.illustrator: Optional[List[CslName]] = normalise_name_list(illustrator)
        self.original_author: Optional[List[CslName]] = normalise_name_list(original_author)
        self.recipient: Optional[List[CslName]] = normalise_name_list(recipient)
        self.reviewed_author: Optional[List[CslName]] = normalise_name_list(reviewed_author)
        self.translator: Optional[List[CslName]] = normalise_name_list(translator)

        self.accessed: Optional[CslDate] = normalise_date(accessed)
        self.container: Optional[CslDate] = normalise_date(container)
        self.event_date: Optional[CslDate] = normalise_date(event_date)
        self.issued: Optional[CslDate] = normalise_date(issued)
        self.original_date: Optional[CslDate] = normalise_date(original_date)
        self.submitted: Optional[CslDate] = normalise_date(submitted)

        self.abstract: Optional[str] = abstract
        self.annote: Optional[str] = annote
        self.archive: Optional[str] = archive
        self.archive_location: Optional[str] = archive_location
        self.archive_place: Optional[str] = archive_place
        self.authority: Optional[str] = authority
        self.call_number: Optional[str] = call_number
        self.chapter_number: Optional[str] = chapter_number
        self.citation_number: Optional[str] = citation_number
        self.citation_label: Optional[str] = citation_label
        self.collection_number: Optional[str] = collection_number
        self.collection_title: Optional[str] = collection_title
        self.container_title: Optional[str] = container_title
        self.container_title_short: Optional[str] = container_title_short
        self.dimensions: Optional[str] = dimensions
        self.DOI: Optional[str] = DOI
        self.edition: Optional[StrNum] = edition
        self.event: Optional[str] = event
        self.event_place: Optional[str] = event_place
        self.first_reference_note_number: Optional[str] = first_reference_note_number
        self.genre: Optional[str] = genre
        self.ISBN: Optional[str] = ISBN
        self.ISSN: Optional[str] = ISSN
        self.issue: Optional[StrNum] = issue
        self.jurisdiction: Optional[str] = jurisdiction
        self.keyword: Optional[str] = keyword
        self.locator: Optional[str] = locator
        self.medium: Optional[str] = medium
        self.note: Optional[str] = note
        self.number: Optional[StrNum] = number
        self.number_of_pages: Optional[str] = number_of_pages
        self.number_of_volumes: Optional[StrNum] = number_of_volumes
        self.original_publisher: Optional[str] = original_publisher
        self.original_publisher_place: Optional[str] = original_publisher_place
        self.original_title: Optional[str] = original_title
        self.page: Optional[str] = page
        self.page_first: Optional[str] = page_first
        self.PMCID: Optional[str] = PMCID
        self.PMID: Optional[str] = PMID
        self.publisher: Optional[str] = publisher
        self.publisher_place: Optional[str] = publisher_place
        self.references: Optional[str] = references
        self.reviewed_title: Optional[str] = reviewed_title
        self.scale: Optional[str] = scale
        self.section: Optional[str] = section
        self.source: Optional[str] = source
        self.status: Optional[str] = status
        self.title: Optional[str] = title
        self.title_short: Optional[str] = title_short
        self.URL: Optional[str] = URL
        self.version: Optional[str] = version
        self.volume: Optional[StrNum] = volume
        self.year_suffix: Optional[StrNum] = year_suffix

        super().__init__()


jso_to_py_names = {
    "article-journal": "article_journal",
    "article-magazine": "article_magazine",
    "article-newspaper": "article_newspaper",
    "entry-dictionary": "entry_dictionary",
    "entry-encyclopedia": "entry_encyclopedia",
    "post-weblog": "post_weblog",
    "review-book": "review_book",
    "dropping-particle": "dropping_particle",
    "non-dropping-particle": "non_dropping_particle",
    "comma-suffix": "comma_suffix",
    "static-ordering": "static_ordering",
    "parse-names": "parse_names",
    "journalAbbreviation": "journal_abbreviation",
    "shortTitle": "short_title",
    "collection-editor": "collection_editor",
    "container-author": "container_author",
    "editorial-director": "editorial_director",
    "original-author": "original_author",
    "reviewed-author": "reviewed_author",
    "event-date": "event_date",
    "original-date": "original_date",
    "archive-location": "archive_location",
    "archive-place": "archive_place",
    "call-number": "call_number",
    "chapter-number": "chapter_number",
    "citation-number": "citation_number",
    "citation-label": "citation_label",
    "collection-number": "collection_number",
    "collection-title": "collection_title",
    "container-title": "container_title_short",
    "date-parts": "date_parts",
    "event-place": "event_place",
    "first-reference-note-number": "first_reference_note_number",
    "number-of-pages": "number_of_pages",
    "number-of-volumes": "number_of_volumes",
    "original-publisher": "original_publisher",
    "original-place": "original_place",
    "original-title": "original_title",
    "page-first": "page_first",
    "publisher-place": "publisher_place",
    "reviewed-title": "reviewed_title",
    "title-short": "title_short",
    "year-suffix": "year_suffix",
}
py_to_jso_names = {v: k for k, v in jso_to_py_names.items()}


class CslNameList:
    @classmethod
    def from_jso(cls, lst):
        return [CslName.from_jso(item) for item in lst]


name_to_class = {
    "type": CslType,
    "author": CslNameList,
    "collection-editor": CslNameList,
    "composer": CslNameList,
    "container-author": CslNameList,
    "director": CslNameList,
    "editor": CslNameList,
    "editorial-director": CslNameList,
    "interviewer": CslNameList,
    "illustrator": CslNameList,
    "original-author": CslNameList,
    "recipient": CslNameList,
    "reviewed-author": CslNameList,
    "translator": CslNameList,
    "container": CslDate,
    "event-date": CslDate,
    "issued": CslDate,
    "original-date": CslDate,
    "submitted": CslDate,
}


def py_to_jso(obj: Any):
    if obj is None:
        return obj

    if isinstance(obj, (bool, Number)):
        return obj

    if isinstance(obj, str):
        return py_to_jso_names.get(obj, obj)

    if isinstance(obj, list):
        return [py_to_jso(item) for item in obj]

    if isinstance(obj, dict):
        d = dict()
        for k, v in obj.items():
            if v is None:
                continue
            key = py_to_jso(k)
            if isinstance(key, Number):
                key = str(Number)
            if not isinstance(key, str):
                raise TypeError("Key of dict is not a string: cannot convert to JSO")
            d[key] = py_to_jso(v)

        return {str(py_to_jso(k)): py_to_jso(v) for k, v in d.items()}

    return obj.to_jso()


def jso_to_py(jso: Any):
    if jso is None:
        return jso

    if isinstance(jso, (bool, Number)):
        return jso

    if isinstance(jso, str):
        return jso_to_py_names.get(jso, jso)

    if isinstance(jso, list):
        return [jso_to_py(item) for item in jso]
    
    if isinstance(jso, dict):
        d = dict()
        for k, v in jso.items():
            key = jso_to_py_names.get(k, k)
            try:
                val = name_to_class[k].from_jso(v)
            except KeyError:
                val = v
            d[key] = val
        return d

    raise ValueError("Given object is not a valid CSL-JSON object")
