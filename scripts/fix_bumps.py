"""Script to convert give times to bumped shows. Run this maybe at like 4AM (when no one is awake hopefully)

Usage
------
python manage.py runscript fix_bumps 

"""
from django.core.mail import send_mail
from scheduler.models import BaseUser, Show, Choice 

def run():
    """Entry point for script."""
    try:
        shows_without_times = Show.objects.filter(day=None, time=None)

        i = 0
        for show in shows_without_times:

            import pdb; pdb.set_trace() 

            i += 1
            dj = show.dj 

            choices = Choice.objects.filter(show=show).exclude(not_available=True)

            if not choices:
                print 'No available choices for this dj: ' + dj
                send_mail(
                    'KWUR Scheduler Additional Times', 
                    'All your choices have been taken! Please enter more here: ' + 
                    'kwur.herokuapp.com/additional-times/' + dj.id,
                    'webmaster@kwur.com',
                    [dj.email],
                    fail_silently=False 
                )

            for choice in choices:
                djs_with_time = Show.objects.filter(day=choice.day, time=choice.time).values_list('dj', flat=True)
                dj_with_time = BaseUser.objects.filter(id__in=djs_with_time).order_by('credits').first()

                print "Dj with time: " + str(dj_with_time)

                existing_show = Show.objects.filter(dj=dj_with_time).first()

                print "Existing show: " + existing_show

                if existing_show:
                    other_credits = dj_with_time.credits 

                    if other_credits < dj.credits:
                        show.day = choice.day
                        show.time = choice.time 
                        show.save()

                        print 'Other Dj got bumped (A): ' + str(dj_with_time)
                        existing_show.day = None 
                        existing_show.time = None 
                        existing_show.save()

                        other_dj_choices = Choice.objects.filter(day=choice.day, time=choice.time)
                        other_dj_choices.update(not_available=True)

                    elif other_credits == dj.credits:

                        if existing_show.timestamp < show.timestamp:
                            choice.not_available = True
                            choice.save()
                        else:
                            show.day = choice.day
                            show.time = choice.time 
                            show.save()

                            print 'Other Dj got bumped (B): ' + str(dj_with_time)
                            existing_show.day = None 
                            existing_show.time = None
                            existing_show.save()

                            other_dj_choices = Choice.objects.filter(day=choice.day, time=choice.time)
                            other_dj_choices.update(not_available=True)

                    else:
                        choice.not_available = True
                        choice.save()

                        if i == choices.count():
                            print 'last choice, need more choices for this dj: ' + dj
                            # Send email to user asking for more times
                            send_mail(
                                'KWUR Scheduler Additional Times', 
                                'All your choices have been taken! Please enter more here: ' + 
                                'kwur.herokuapp.com/additional-times/' + dj.id,
                                'webmaster@kwur.com',
                                [dj.email],
                                fail_silently=False 
                            )
                else:
                    print show + ' show successfully saved with day and time'
                    show.day = choice.day
                    show.time = choice.time
                    show.save()

                    other_dj_choices = Choice.objects.filter(day=choice.day, time=choice.time)
                    other_dj_choices.update(not_available=True)


    except Exception, e:
        print "A problem arose"
        raise e