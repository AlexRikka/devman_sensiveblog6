from django.shortcuts import render
from blog.models import Post, Tag
from django.db.models import Count, Min
from django.shortcuts import get_object_or_404


def serialize_post(post):
    return {
        'title': post.title,
        'teaser_text': post.text[:200],
        'author': post.author.username,
        'comments_amount': post.comments_count,
        'image_url': post.image.url if post.image else None,
        'published_at': post.published_at,
        'slug': post.slug,
        'tags': [serialize_tag(tag) for tag in post.tags.popular()],
        'first_tag_title': post.tag_title,
    }


def serialize_tag(tag):
    return {
        'title': tag.title,
        'posts_with_tag': tag.posts_count,
    }


def index(request):
    most_popular_posts = Post.objects.popular()[:5] \
        .fetch_with_comments_count()

    fresh_posts = Post.objects \
        .order_by('-published_at') \
        .annotate(
            comments_count=Count('comments', distinct=True),
            tag_title=Min('tags__title')) \
        .select_related('author')
    most_fresh_posts = list(fresh_posts[:5])

    most_popular_tags = list(
        Tag.objects.popular()[:5])

    context = {
        'most_popular_posts': [serialize_post(post)
                               for post in most_popular_posts],
        'page_posts': [serialize_post(post)
                       for post in most_fresh_posts],
        'popular_tags': [serialize_tag(tag)
                         for tag in most_popular_tags],
    }
    return render(request, 'index.html', context)


def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug)

    comments = post.comments.select_related('author').all()
    serialized_comments = []
    for comment in comments:
        serialized_comments.append({
            'text': comment.text,
            'published_at': comment.published_at,
            'author': comment.author.username,
        })

    likes = post.likes.all()
    related_tags = post.tags.popular()

    serialized_post = {
        'title': post.title,
        'text': post.text,
        'author': post.author.username,
        'comments': serialized_comments,
        'likes_amount': likes.count,
        'image_url': post.image.url if post.image else None,
        'published_at': post.published_at,
        'slug': post.slug,
        'tags': [serialize_tag(tag) for tag in related_tags],
    }

    most_popular_tags = list(
        Tag.objects.popular()[:5])

    most_popular_posts = Post.objects.popular()[:5] \
        .fetch_with_comments_count()

    context = {
        'post': serialized_post,
        'popular_tags': [serialize_tag(tag)
                         for tag in most_popular_tags],
        'most_popular_posts': [
            serialize_post(post) for post in most_popular_posts
        ],
    }
    return render(request, 'post-details.html', context)


def tag_filter(request, tag_title):
    tag = get_object_or_404(Tag.objects.filter(title=tag_title))

    most_popular_tags = list(
        Tag.objects.popular()[:5])

    most_popular_posts = Post.objects.popular()[:5] \
        .fetch_with_comments_count()

    related_posts = tag.posts.prefetch_related('tags') \
        .fetch_with_comments_count()[:20]

    context = {
        'tag': tag.title,
        'popular_tags': [serialize_tag(tag)
                         for tag in most_popular_tags],
        'posts': [serialize_post(post) for post in related_posts],
        'most_popular_posts': [
            serialize_post(post) for post in most_popular_posts
        ],
    }
    return render(request, 'posts-list.html', context)


def contacts(request):
    # позже здесь будет код для статистики заходов на эту страницу
    # и для записи фидбека
    return render(request, 'contacts.html', {})
