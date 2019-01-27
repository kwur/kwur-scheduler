# -*- coding: utf-8 -*-
from django.shortcuts import render, redirect
from django.http import HttpResponse
from datetime import datetime 
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from decimal import Decimal

from .models import BaseUser, Show, Choice, Crediting


def index(request):
	"""
	Index will show either the form or, when the form will no longer be used, a 
	statement saying that scheduling is closed.
	"""

	# return render(request, 'index.html', {})

	#uncomment this line and comment the above line once we cut off scheduling
	return render(request, 'cannot_schedule_anymore.html', {})

def time_is_valid(request, day, time, name):
	"""
	Checks if the user submitted a valid time. Make sure that the logic statements here 
	align with current KWUR show policy (may include blacking out times for George's show).
	"""

	if ((day != '0' and day != '6') and time.hour == 21) or time.minute != 0:
		return False

	# George's time
	if name != "George Yeh" and day == '6' and time.hour >= 9 and time.hour < 12:
		return False

	return True


def submit_show(request):
	"""
	Submits the information from the form into the database to give the user a tentative 
	time for show. If first choice is taken, the scheduler will go to the second choice. 
	If second is taken, to the third choice. If all choices are taken, the user will not 
	have a showtime temporarily. This will be resolved once the script to bump/assign shows 
	is ran. 
	"""

	unknown_dj = BaseUser.objects.get(first_name__iexact='Unknown', last_name__iexact='Dj')

	first_name = request.POST.get('first_name').strip()
	last_name = request.POST.get('last_name').strip()
	email = request.POST.get('email').strip()
	show_name = request.POST.get('show_name').strip()
	genre = request.POST.get('genre').strip()
	tagline = request.POST.get('tagline').strip()
	first_choice_day = request.POST.get('first_choice_day')
	first_choice_time = request.POST.get('first_choice_time')
	second_choice_day = request.POST.get('second_choice_day')
	second_choice_time = request.POST.get('second_choice_time')
	third_choice_day = request.POST.get('third_choice_day')
	third_choice_time = request.POST.get('third_choice_time')
	co_dj = request.POST.get('co_dj')

	full_name = first_name + " " + last_name
	
	if not first_choice_time == "":
		first_choice_time = datetime.strptime(first_choice_time, '%I:%M %p').time()
		if not time_is_valid(request, first_choice_day, first_choice_time, full_name):
			return render(request, 'invalid_times.html', {})


	if not second_choice_time == "":
		second_choice_time = datetime.strptime(second_choice_time, '%I:%M %p').time()
		if not time_is_valid(request, second_choice_day, second_choice_time, full_name):
			return render(request, 'invalid_times.html', {})

	if not third_choice_time == "":
		third_choice_time = datetime.strptime(third_choice_time, '%I:%M %p').time()
		if not time_is_valid(request, third_choice_day, third_choice_time, full_name):
			return render(request, 'invalid_times.html', {})

	# Finds the DJ in the BaseUser database and saves their email
	dj = BaseUser.objects.filter(first_name__iexact=first_name, last_name__iexact=last_name).first()

	if not dj:
		first_name_matches = BaseUser.objects.filter(first_name__iexact=first_name)
		last_name_matches = BaseUser.objects.filter(last_name__iexact=last_name)
		# merge the two together into unique query set
		potential_results = first_name_matches | last_name_matches
		# takes user to a page asking if any of the names given is theirs if their name cannot be found
		#  in BaseUser database 
		return render(request, 'not_in_database.html', {
			'potential_results': potential_results
		})

	dj.email = email
	dj.save()


	# Adds co-dj to show if co-dj exists 
	if co_dj == '':
		co_dj = None 
	else:
		co_dj_full_name = co_dj.lower().split()
		fname = co_dj_full_name[0]
		lname = co_dj_full_name[1]
		co_dj = BaseUser.objects.filter(first_name__iexact=fname, last_name__iexact=lname).first()

		# take into consideration if Co DJ doesn't exist 
		if not co_dj:
			# If any unknown_djs are in the database, check to see why this user doesn't exist
			co_dj = unknown_dj 


	# Create Show for dj if show doesn't exist
	show = Show.objects.filter(dj=dj).first()

	if not show: 
		show = Show(show_name=show_name, dj=dj, co_dj=co_dj, genre=genre, tagline=tagline)
		show.save()
	

	# Saves dj's choices in case they get bumped by someone with higher credits in the Credits database
	first_choice = Choice(show=show, choice_num=0, day=first_choice_day, 
						  time=first_choice_time)
	first_choice.save()

	choices = [first_choice]

	if second_choice_day and second_choice_time:
		second_choice = Choice(show=show, choice_num=1, day=second_choice_day,
							   time=second_choice_time)
		second_choice.save()

		choices.append(second_choice)

	if third_choice_day and third_choice_time:
		third_choice = Choice(show=show, choice_num=2, day=third_choice_day,
							  time=third_choice_time)
		third_choice.save()

		choices.append(third_choice)


	format = '%H:%M %p'

	# This variable checks what choice we are on while looping through the choices given by the dj
	i = 0

	# Check if any of those choices are already taken 
	for choice in choices:
		i += 1
		djs_with_this_choice = Show.objects.filter(day=choice.day, time=choice.time).values_list('dj', flat=True)
		dj_with_time = BaseUser.objects.filter(id__in=djs_with_this_choice).order_by('credits').first()

		existing_show = Show.objects.filter(dj=dj_with_time).first()

		# Compares the number of credits our current user submitting show has against the other user's
		# which currently has this showtime. 
		if existing_show and (existing_show.dj != dj): 
			other_dj_credits = dj_with_time.credits

			if other_dj_credits < dj.credits: 

				# Current user steals the other dj's time 
				show.day = choice.day
				show.time = choice.time 
				show.save() 

				existing_show.day = None
				existing_show.time = None
				existing_show.save()

				# Marks this show time as unavailable for anybody else who has this choice 
				other_dj_choices = Choice.objects.filter(day=choice.day, time=choice.time)
				other_dj_choices.update(not_available=True)

				return render(request, 'thank_for_submissions.html', {})
			else: 
				choice.not_available = True
				choice.save()

				# All choices are taken at this point, so redirect user to 
				# a page that asks for more choices 
				if i == 3: 
					return render(request, 'additional_times.html', {
						'dj': dj,
						'choices': choices,
					})

		# Time is free and can be assigned to user's show 
		else: 
			show.day = choice.day 
			show.time = choice.time 
			show.save()

			other_dj_choices = Choice.objects.filter(day=choice.day, time=choice.time)
			other_dj_choices.update(not_available=True)

			return render(request, 'thank_for_submissions.html', {})

	return render(request, 'additional_times.html', {
		'dj': dj,
		'choices': choices,
	})


def additional_times(request, dj_id):
	"""
	Users are directed to this page once they receive an email stating that they were bumped. 
	This page will ask the user for more show time choices.
	"""

	dj_id = int(dj_id)
	dj = BaseUser.objects.filter(id=dj_id).first()

	show = Show.objects.filter(dj=dj).first()

	# This will be used to display the user's previous choices so that they won't resubmit the same 
	# time slots
	if show:
		choices = Choice.objects.filter(show=show)
	else:
		choices = []

	return render(request, 'additional_times.html', {
		'dj': dj, 
		'choices': choices
	})

def submit_additional_times(request, dj_id):
	"""
	This function saves the additional times entered and assigns a time for the user if the time 
	is available. 
	"""

	dj_id = int(dj_id)
	dj = BaseUser.objects.filter(id=dj_id).first()

	show = Show.objects.filter(dj=dj).first()

	if show:
		last_choice = Choice.objects.filter(show=show).order_by('choice_num').last()

		if last_choice:
			choice_num = last_choice.choice_num
		else:
			choice_num = 0

		first_choice_day = request.POST.get('choice_one_day')
		first_choice_time = request.POST.get('choice_one_time')
		second_choice_day = request.POST.get('choice_two_day')
		second_choice_time = request.POST.get('choice_two_time')
		third_choice_day = request.POST.get('choice_three_day')
		third_choice_time = request.POST.get('choice_three_time')

		if not first_choice_time == "":
			first_choice_time = datetime.strptime(first_choice_time, '%I:%M %p').time()
			if not time_is_valid(request, first_choice_day, first_choice_time, "not George"):
				return render(request, 'invalid_times.html', {})


		if not second_choice_time == "":
			second_choice_time = datetime.strptime(second_choice_time, '%I:%M %p').time()
			if not time_is_valid(request, second_choice_day, second_choice_time, "not George"):
				return render(request, 'invalid_times.html', {})

		if not third_choice_time == "":
			third_choice_time = datetime.strptime(third_choice_time, '%I:%M %p').time()
			if not time_is_valid(request, third_choice_day, third_choice_time, "not George"):
				return render(request, 'invalid_times.html', {})



		if first_choice_day and first_choice_time: 
			first_choice = Choice(show=show, choice_num=(choice_num+1), day=first_choice_day, 
								  time=first_choice_time)
			first_choice.save()

		if second_choice_day and second_choice_time:
			second_choice = Choice(show=show, choice_num=(choice_num+2), day=second_choice_day,
								   time=second_choice_time)
			second_choice.save()

		if third_choice_day and third_choice_time:
			third_choice = Choice(show=show, choice_num=(choice_num+3), day=third_choice_day,
								  time=third_choice_time)
			third_choice.save()

		return render(request, 'thank_for_submissions.html', {})

	else:
		return redirect('index')

def tentative_schedule(request):
	"""
	This will display the tentative schedule for the users who have submitted their showtimes.
	"""
	
	shows_dict = {
		0: [], 
		1: [],
		2: [],
		3: [], 
		4: [], 
		5: [], 
		6: []
	}

	for i in range(7):
		for show in Show.objects.filter(day=i).order_by('time'):
				show_time = show.time
				dj = str(show.dj)
				if show.co_dj and str(show.co_dj) != "Unknown Dj":
					dj += " & " + str(show.co_dj)
				shows_dict[i].append([dj, show_time.strftime('%I:%M %p')])

	return render(request, 'tentative_schedule.html', {
			'shows_dict': shows_dict 
	})

def schedule_with_names(request):
	shows_dict = {
		0: [], 
		1: [],
		2: [],
		3: [], 
		4: [], 
		5: [], 
		6: []
	}

	for i in range(7):
		for show in Show.objects.filter(day=i).order_by('time'):
				show_time = show.time 
				shows_dict[i].append([str(show.show_name), show_time.strftime('%I:%M %p')])

	return render(request, 'tentative_schedule.html', {
			'shows_dict': shows_dict 
	})

def login_page(request):
	return render(request, 'login.html', {})

def crediting(request):
	username = request.POST['username']
	password = request.POST['password']

	user = authenticate(username=username, password=password)

	if user is not None:
		login(request, user)
		return render(request, 'crediting.html', {})
	else:
		return render(request, 'invalid_login.html', {})

def submit_credits(request):
	first_name = request.POST.get('first_name')
	last_name = request.POST.get('last_name')
	credits = request.POST.get('credits')
	exec_email = request.POST.get('exec-email')
	crediting_reason = request.POST.get('crediting-reason')

	dj = BaseUser.objects.filter(first_name=first_name, last_name=last_name).first()

	if dj:
		credits = int(credits)
		crediting = Crediting(dj=dj, credits=credits, crediting_reason=crediting_reason, exec_email=exec_email)
		crediting.save()

		if credits < 0:
			send_mail(
                'You\'ve been decredited', 
                'Seems like you\'ve lost some credits! If you want to know why, send an email to ' + exec_email + '. Reason for decrediting: ' + crediting_reason + '.', 
                'webmaster@kwur.com',
                [dj.email],
                fail_silently=False 
            )
	else:
		return render(request, 'not_in_database.html', {'for_crediting': True})

	return render(request, 'thank_for_submissions.html', {})

def view_credits(request):
	creditings = Crediting.objects.all()
	return render(request, 'finalize_credits.html', {
		'creditings': creditings
	})

def finalize_creditings(request):
	accepted_creditings = request.POST.getlist('accept')
	num_credits = request.POST.getlist('num_credits')
	creditings = request.POST.getlist('crediting')
	
	if accepted_creditings:
		for i in range(len(accepted_creditings)):
			dj = BaseUser.objects.get(id=int(accepted_creditings[i]))
			if dj: 
				dj.credits += Decimal(num_credits[i])
				if dj.credits < 0:
					dj.credits = 0 
				dj.save()
				# delete crediting 
				crediting = Crediting.objects.get(id=int(creditings[i]))
				crediting.delete()


	return render(request, 'thank_for_submissions.html', {})


