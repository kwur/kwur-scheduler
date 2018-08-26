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

        for show in shows_without_times:

            dj = show.dj 
            print "Show: " + show.encode('utf-8') + " Dj: " + dj.encode('utf-8')

            choices = Choice.objects.filter(show=show).exclude(not_available=True)

            if not choices:
                print 'No available choices for this dj: ' + dj.encode('utf-8')
                send_mail(
                     'KWUR Scheduler Additional Times', 
                     'All of your choices have been taken! Please enter more here: ' + 
                     'kwur.herokuapp.com/additional-times/' + str(dj.id) + '.' + 
                     ' Here\'s the link to the tentative schedule we have so far: kwur.herokuapp.com/tentative-schedule',
                     'webmaster@kwur.com',
                     [dj.email, 'webmaster@kwur.com'],
                     fail_silently=False 
                )

            i = 0
            for choice in choices:
                i += 1
                djs_with_time = Show.objects.filter(day=choice.day, time=choice.time).values_list('dj', flat=True)
                dj_with_time = BaseUser.objects.filter(id__in=djs_with_time).order_by('credits').first()

                existing_show = Show.objects.filter(dj=dj_with_time).first()

                if existing_show:
                    other_credits = dj_with_time.credits 

                    if other_credits < dj.credits:
                        show.day = choice.day
                        show.time = choice.time 
                        show.save()

                        print 'Other Dj got bumped (A): ' + dj_with_time.encode('utf-8')
                        existing_show.day = None 
                        existing_show.time = None 
                        existing_show.save()

                        # User has taken this time, all other djs with this time choice cannot have it
                        other_dj_choices = Choice.objects.filter(day=choice.day, time=choice.time)
                        other_dj_choices.update(not_available=True)

                        break 

                    elif other_credits == dj.credits:

                        if existing_show.timestamp < show.timestamp:
                            choice.not_available = True
                            choice.save()
                        else:
                            show.day = choice.day
                            show.time = choice.time 
                            show.save()

                            print 'Other Dj got bumped (B): ' + dj_with_time.encode('utf-8')
                            existing_show.day = None 
                            existing_show.time = None
                            existing_show.save()

                            # User has taken this time, all other djs with this time choice cannot have it
                            other_dj_choices = Choice.objects.filter(day=choice.day, time=choice.time)
                            other_dj_choices.update(not_available=True)

                            break 

                    else:
                        choice.not_available = True
                        choice.save()

                        if i == choices.count():
                            print 'Last choice, need more choices for this dj: ' + dj.encode('utf-8')
                            # Send email to user asking for more times
                            send_mail(
                                 'KWUR Scheduler Additional Times', 
                                 'All of your choices have been taken! Please enter more here: ' + 
                                 'kwur.herokuapp.com/additional-times/' + str(dj.id) + '.' + 
                                 ' Here\'s the link to the tentative schedule we have so far: kwur.herokuapp.com/tentative-schedule',
                                 'webmaster@kwur.com',
                                 [dj.email, 'webmaster@kwur.com'],
                                 fail_silently=False 
                            )
                else:
                    print show.encode('utf-8') + ' show successfully saved with day and time'
                    show.day = choice.day
                    show.time = choice.time
                    show.save()


                    # Sets that choice and other choices with that time to not available
                    other_dj_choices = Choice.objects.filter(day=choice.day, time=choice.time)
                    other_dj_choices.update(not_available=True)

                    break


    except Exception, e:
        print "A problem arose:"
        print str(e)
        raise e
