import datetime
from django.shortcuts import render
from read_statistics.utils import get_seven_days_read_data, get_today_hot_date, get_yesterday_hot_date
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.db.models import Sum
from django.core.cache import cache
from blog.models import Blog



def get_sevendays_hot_blogs():
    today = timezone.now().date()
    date = today - datetime.timedelta(days=7)
    blogs = Blog.objects.filter(read_details__date__lt=today, read_details__date__gte=date) \
                        .values('id', 'title')\
                        .annotate(read_num_sum=Sum('read_details__read_num'))\
                        .order_by('-read_num_sum')
    return blogs[:7]


def home(request):
    blog_content_type = ContentType.objects.get_for_model(Blog)
    dates, read_nums = get_seven_days_read_data(blog_content_type)

    # 获取7天热门数据
    sevendays_hot_date = cache.get('sevendays_hot_date')
    if sevendays_hot_date is None:
        sevendays_hot_date = get_sevendays_hot_blogs()
        cache.set('sevendays_hot_date', sevendays_hot_date, 60*60)

    context = {}
    context['dates'] = dates
    context['read_nums'] = read_nums
    context['today_hot_date'] = get_today_hot_date(blog_content_type)
    context['yesterday_hot_date'] = get_yesterday_hot_date(blog_content_type)
    context['sevendays_hot_date'] = get_sevendays_hot_blogs()
    return render(request, 'home.html', context)


