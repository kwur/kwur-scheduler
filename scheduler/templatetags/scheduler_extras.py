from django import template

register = template.Library()

@register.filter(name='get_day_of_week')
def get_day_of_week(day):
	
	day = int(day)

	DAYS_OF_WEEK = {
		0: 'Sunday', 
		1: 'Monday', 
		2: 'Tuesday',
		3: 'Wednesday', 
		4: 'Thursday', 
		5: 'Friday', 
		6: 'Saturday'
	}
	
	return DAYS_OF_WEEK.get(day)