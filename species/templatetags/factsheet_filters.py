from django import template
from django.db.models import Min, Max
from django.utils.safestring import mark_safe
from django.template.defaultfilters import stringfilter

try:
    from ..models import State, Species, SpeciesRecord, GlossaryWord
except Exception:
    pass
import json, re

register = template.Library()

@register.filter
def get_records(value):
    results = list(SpeciesRecord.objects.filter(species=value).select_related('collector__name', 'collection__url', 'collection__name', 'county_name', 'state__code').values('collection__name', 'collection__url', 'collector__name', 'county__name', 'day', 'elevation', 'females', 'id', 'latitude', 'longitude', 'locality', 'linked_photo', 'males', 'month', 'notes', 'record_type', 'state__code', 'subspecies', 'year'))

    renames = ['collection', 'collector', 'county']
    for d in results:
        # rename for json output
        for r in renames:
            d[r] = d["%s__name" % r]
            del d["%s__name" % r]
        # rename state, duplicate locality, add date
        d['state'] = d['state__code']
        del d['state__code']
        if d['county'] and d['state']:
            d['county'] += " (%s)" % d['state']
        d['site_name'] = d['locality']
        d['date'] = "%s/%s/%s" % (d['year'], d['month'], d['day'])
        if d['latitude']:
            d['latitude'] = "{0:.2f}".format(float(d['latitude']))
        if d['longitude']:
            d['longitude'] = "{0:.2f}".format(float(d['longitude']))

    return json.dumps(results)

@register.filter
def get_photos(value):
    records = list(value.get_ordered_images())
    entries = []
    for photo in records:
        if photo.record:
            entries.append({'record_id': photo.record.id, 'url': photo.thumbnail_url()})
    return json.dumps(entries)

@register.filter
def filters_json(value, arg):
    """
        Returns Array with extra values removed based on species
    """
    def _human_key(key):
        parts = re.split('(\d*\.\d+|\d+)', key)
        return tuple((e.swapcase() if i % 2 == 0 else float(e)) for i, e in enumerate(parts))

    if arg == "county":
        states = list(State.objects.all().values_list())
        state_lookup = dict()
        for p in states:
            s_id,code = p
            state_lookup[s_id] = code
        return str(sorted([str("%s (%s)" % (item[0], state_lookup.get(item[1], "CANADA"))).replace("'", "`") for item in set(value.speciesrecord_set.all().values_list('county__name', 'county__state'))])).replace("'", '"').replace("`", "'")
        
    # filter removes None elements, human sort sorts in expected order
    return str(sorted([str(str(item)[0].capitalize() + str(item)[1:]).replace("'", "`") for item in set(filter(None, value.speciesrecord_set.all().values_list(arg, flat=True)))], key=_human_key)).replace("'", '"').replace("`", "'")

@register.filter
def glossary_words_json(value):
    """
    Returns a JSON object of glossary information
    """
    gw = list(GlossaryWord.objects.values())
    gw.sort(key=lambda s: len(str(s['word'])), reverse=True)
    return json.dumps(gw)

@register.filter
def range_values(value):
    elevations = SpeciesRecord.objects.filter(species=value).aggregate(Max('elevation'), Min('elevation')) 
    elevations["elevation__min"] = elevations["elevation__min"] or 0
    elevations["elevation__max"] = elevations["elevation__max"] or 14000
    # can't be equal for range filter
    if elevations["elevation__max"] == elevations["elevation__min"]:
        elevations["elevation__max"] += 1

    if SpeciesRecord.objects.filter(species=value).filter(year__isnull=False).order_by("year", "month", "day").count() > 0:
        min_date = SpeciesRecord.objects.filter(species=value).filter(year__isnull=False).order_by("year", "month", "day")[0].fuzzy_date
    else:
        min_date = None
    if min_date:
        min_date = "%02d/%02d/%02d" % (min_date.month, min_date.day, min_date.year)
    else:
        min_date = "01/01/1890"

    if SpeciesRecord.objects.filter(species=value).filter(year__isnull=False).order_by("year", "month", "day").count() > 0:
        max_date = SpeciesRecord.objects.filter(species=value).filter(year__isnull=False).order_by("year", "month", "day").reverse()[0].fuzzy_date
    else:
        max_date = None
    if max_date:
        max_date = "%02d/%02d/%02d" % (max_date.month, max_date.day, max_date.year)
    else:
        max_date = "01/01/1890"

    dates ={"dates__min": min_date,
            "dates__max": max_date}

    elevations.update(dates)
    return json.dumps(elevations)

@register.filter
def states_list(value):
    """
    Returns html for populating state multiselect box
    """
    states = set(SpeciesRecord.objects.all().exclude(state__code=None).values_list("state__code", flat=True))

    states = sorted(states)

    html = ""
    
    for state in states:
        
        html += "\t<option value=\"" + str(state) + "\">" + str(state) + "</option>\n"

    return mark_safe(html)

@register.filter
def counties_list(value):
    """
    Returns html for populating county multiselect box
    """
    states = set(SpeciesRecord.objects.all().exclude(state__code=None).values_list("state__code", flat=True))

    states = sorted(states)

    html = ""
    
    for state in states:
        html += "\t<optgroup label=\"" + str(state) + "\" class=\"countySel " + str(state) + "\">\n"
        counties = set(SpeciesRecord.objects.filter(county__state__code=str(state)).exclude(county__name=None).values_list("county__name", flat=True))
        counties = sorted(counties)

        for county in counties:
            html += "\t\t<option value=\"" + str(county) + "\">" + str(county) + "</option>\n"

    return mark_safe(html)

@register.filter
@stringfilter
def loc_class(value):
    """
    Rerturns the states and counties the species is found in
    """
    genus, species = value.rsplit(" ", 1)

    q1 = SpeciesRecord.objects.filter(species__genus=genus)

    states = set(q1.filter(species__species=species).exclude(state__code=None).values_list("state__code", flat=True))

    counties = set(q1.filter(species__species=species).exclude(county__name=None).values_list("county__name", "county__state__code"))

    countiesNS = set()

    for county in counties:
        countiesNS.add(county[0].replace(" ", "") + county[1])

    statesStr = str(" ".join(states))

    countiesStr = str(" ".join(countiesNS))

    return statesStr + " " + countiesStr

@register.filter
@stringfilter
def li_level(value):
    """
    Returns the name of the level the li is on
    """
    split = value.split(" ")

    if len(split) == 1:
        return "Genus"
    elif len(split) == 2:
        return "Species "
    else:
        return split[0];
