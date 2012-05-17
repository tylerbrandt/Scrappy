from django import template
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe
import calendar

register = template.Library()

@register.filter(needs_autoescape=True)
def nav_ul(l, nesting=0, autoescape=None):
	"""Works like unordered_list, except makes each element link to referenced element"""
	
	# determine the correct class based on nesting level
	nesting_level = ['year', 'month', 'day', 'entry']

	if autoescape:
		esc = conditional_escape
	else:
		esc = lambda x: x

	s = ''
	if hasattr(l, 'iteritems'):
		# convert the dictionary-like object into a ul
		s = '<ul>'
		for key, value in l.iteritems():
			label = nesting_level[nesting]
			dispVal = esc(key)
			if label == 'month':
				dispVal = calendar.month_name[key]
			s += '<li><a class="%s" href="#nav_%s_%s">%s</a>%s</li>' % (label, label, esc(key), dispVal, nav_ul(value, nesting=nesting+1))
		s += '</ul>'

	# Ignore non-dictionary results
	# elif type(l) == list:
	# 	s = '<ul>' + ''.join([nav_ul(item, nesting=nesting) for item in l]) + '</ul>'

	# else:
	# 	s = '<li><a class="%s" href="#nav_%s">%s</a></li>' % (nesting_level[nesting], l.id, esc(l))

	return mark_safe(s)
		