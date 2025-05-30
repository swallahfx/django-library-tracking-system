from celery import shared_task
from .models import Loan
from django.core.mail import send_mail
from django.conf import settings
from datetime import timedelta, datetime

@shared_task
def send_loan_notification(loan_id):
    try:
        loan = Loan.objects.get(id=loan_id)
        member_email = loan.member.user.email
        book_title = loan.book.title
        send_mail(
            subject='Book Loaned Successfully',
            message=f'Hello {loan.member.user.username},\n\nYou have successfully loaned "{book_title}".\nPlease return it by the due date.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[member_email],
            fail_silently=False,
        )
    except Loan.DoesNotExist:
        pass

@shared_task
def send_overdue_notification(member, overdue_loans):
    try:
        member_email = member.user.email
        book_titles = ', '.join([loan.book.title for loan in overdue_loans])
        send_mail(
            subject='Overdue Book Notification',
            message=f'Hello {member.user.username},\n\nThe following books are overdue: {book_titles}.\nPlease return them as soon as possible.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[member_email],
            fail_silently=False,
        )
        print(f"Overdue notification sent to {member.user.username} for books: {book_titles}")
    except Exception as e:
        print(f"Error sending overdue notification: {str(e)}")

@shared_task
def check_overdue_loans():
    try:
        get_overdue_loans = Loan.objects.filter(
            is_returned=False, 
            due_date__lt=datetime.now().date()
        ).select_related('member', 'book')

        overdue = get_overdue_loans.count()
        if not overdue:
            return "No overdue loans found."
        
        overdue_members = set(i.member for i in get_overdue_loans)
        for member in overdue_members:
            member_overdue_loans = get_overdue_loans.filter(member=member)
            send_overdue_notification(member, member_overdue_loans)
    except Exception as e:
        return f"Error checking overdue loans: {str(e)}"
    except Loan.DoesNotExist:
        return "No loans found."
