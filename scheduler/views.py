from django.shortcuts import render, redirect
from django.http import HttpResponse
from datetime import datetime 

from .models import BaseUser, Show, Choice

def index(request):
	return render(request, 'index.html', {})

def submit_show(request):
	unknown_dj = BaseUser.objects.get(id=316)

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
	
	nine_pm = datetime.strptime('09:00 PM', '%I:%M %p').time()
	eleven_pm = datetime.strptime('11:00 PM', '%I:%M %p').time() 

	if not first_choice_time == "":
		first_choice_time = datetime.strptime(first_choice_time, '%I:%M %p').time()

	if not second_choice_time == "":
		second_choice_time = datetime.strptime(second_choice_time, '%I:%M %p').time()

	if not third_choice_time == "":
		third_choice_time = datetime.strptime(third_choice_time, '%I:%M %p').time() 

	# Rather than creating a new user, find existing baseuser and save their email
	dj = BaseUser.objects.filter(first_name__iexact=first_name, last_name__iexact=last_name).first()

	if not dj:
		return render(request, 'not_in_database.html', {})

	dj.email = email
	dj.save()

	if co_dj == '':
		co_dj = None 
	else:
		co_dj_list = co_dj.lower().split()
		fname = co_dj_list[0]
		lname = co_dj_list[1]
		co_dj = BaseUser.objects.filter(first_name__iexact=fname, last_name__iexact=lname).first()

		# take into consideration if Co DJ doesn't exist 
		if not co_dj:
			# If any unknown_djs are in the database, check to see why this base user doesn't exist
			co_dj = unknown_dj 

	show = Show.objects.filter(dj=dj).first()

	# If show doesn't exist, create show 
	if not show: 
		show = Show(show_name=show_name, dj=dj, co_dj=co_dj, genre=genre, tagline=tagline)
		show.save()
	
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

	# This variable is used to check if a choice is the last choice given 
	# by the dj or not

	i = 0

	# Check if any of those choices are already taken 
	for choice in choices:
		i += 1
		djs_with_time = Show.objects.filter(day=choice.day, time=choice.time).values_list('dj', flat=True)
		dj_with_time = BaseUser.objects.filter(id__in=djs_with_time).order_by('credits').first()

		existing_show = Show.objects.filter(dj=dj_with_time).first()

		if existing_show: 
			other_dj_credits = dj_with_time.credits

			if other_dj_credits < dj.credits: 

				# Current user steals the other dj's time 
				show.day = choice.day
				show.time = choice.time 
				show.save() 

				existing_show.day = None
				existing_show.time = None
				existing_show.save()

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
	dj_id = int(dj_id)
	dj = BaseUser.objects.filter(id=dj_id).first()

	show = Show.objects.filter(dj=dj).first()

	if show:
		choices = Choice.objects.filter(show=show)
	else:
		choices = []

	return render(request, 'additional_times.html', {
		'dj': dj, 
		'choices': choices
	})

def submit_additional_times(request, dj_id):
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

		if first_choice_day and first_choice_time: 
			first_choice_time = datetime.strptime(first_choice_time, '%I:%M %p').time()
			first_choice = Choice(show=show, choice_num=(choice_num+1), day=first_choice_day, 
								  time=first_choice_time)
			first_choice.save()

		if second_choice_day and second_choice_time:
			second_choice_time = datetime.strptime(second_choice_time, '%I:%M %p').time()
			second_choice = Choice(show=show, choice_num=(choice_num+2), day=second_choice_day,
								   time=second_choice_time)
			second_choice.save()

		if third_choice_day and third_choice_time:
			third_choice_time = datetime.strptime(third_choice_time, '%I:%M %p').time() 
			third_choice = Choice(show=show, choice_num=(choice_num+3), day=third_choice_day,
								  time=third_choice_time)
			third_choice.save()

		return render(request, 'thank_for_submissions.html', {})

	else:
		return redirect('index')
