

from django.db import models
from datetime import datetime 
from django.utils.encoding import smart_text

DAYS_OF_WEEK = {
	0: 'Sunday', 
	1: 'Monday', 
	2: 'Tuesday',
	3: 'Wednesday', 
	4: 'Thursday', 
	5: 'Friday', 
	6: 'Saturday'
}

class BaseUser(models.Model):
	first_name = models.CharField(max_length=25)
	last_name = models.CharField(max_length=30)
	credits = models.DecimalField(default=0, max_digits=6, decimal_places=2)
	email = models.EmailField(default='', blank=True, null=True)

	def __str__(self):
		return self.first_name + ' ' + self.last_name

class Show(models.Model):
	show_name = models.CharField(max_length=200)
	dj = models.ForeignKey(BaseUser, on_delete=models.CASCADE)
	co_dj = models.ForeignKey(BaseUser, null=True, blank=True, related_name='co_dj', on_delete=models.CASCADE)
	genre = models.CharField(max_length=50)
	tagline = models.TextField()
	day = models.IntegerField(blank=True, null=True)
	time = models.TimeField(blank=True, null=True)
	timestamp = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		format = '%I:%M %p'
		if not (self.day == None and self.time == None):
			return self.show_name + '-' + str(self.dj) + '-' + DAYS_OF_WEEK[self.day] + " " + self.time.strftime(format)
		else: 
			return self.show_name + '-' + str(self.dj)

	def __unicode__(self):
		format = '%I:%M %p'
		if not (self.day == None and self.time == None):
			temp = self.show_name + '-' + str(self.dj) + '-' + DAYS_OF_WEEK[self.day] + " " + self.time.strftime(format)
			return '%s' % (temp)
		else: 
			temp = self.show_name + '-' + str(self.dj)
			return '%s' % (temp)

class Choice(models.Model):
	show = models.ForeignKey(Show, on_delete=models.CASCADE)
	choice_num = models.IntegerField(default=0)
	day = models.IntegerField(default=0)
	time = models.TimeField()
	not_available = models.BooleanField(default=False)

	def __str__(self):
		format = '%I:%M %p'
		return self.show.show_name + '-' + str(self.show.dj) + '-' + DAYS_OF_WEEK[self.day] + '-' + self.time.strftime(format)

	def __unicode__(self):
		format = '%I:%M %p'
		temp = self.show.show_name + '-' + str(self.show.dj) + '-' + DAYS_OF_WEEK[self.day] + '-' + self.time.strftime(format)
		return '%s' % (temp)

class Crediting(models.Model):
	dj = models.ForeignKey(BaseUser, on_delete=models.CASCADE)
	credits = models.DecimalField(default=0, max_digits=5, decimal_places=2)
	crediting_reason = models.TextField()
	exec_email = models.EmailField(default='', blank=True, null=True)

	def __str__(self):
		return str(self.dj) + ' ' + str(self.credits)