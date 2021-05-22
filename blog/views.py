from datetime import timezone
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from .models import Post, Comment
from .forms import PostForm, CommentForm
from django.utils import timezone
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views.generic import (
    TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView)


# Create your views here.
class AboutView(TemplateView):
    template_name = "about.html"


class PostListView(ListView):
    model = Post
    # by default: template_name = "post_list.html"

    def get_queryset(self):
        #      Post.objects.filter(published_date__lte=timezone.now())
        # sql: SELECT * FROM Post WHERE published_date <= timezone.now();
        # -published_date => to make the most recent posts comes first
        return Post.objects.filter(published_date__lte=timezone.now()).order_by('-published_date')


class PostDetailView(DetailView):
    model = Post
    # default: template_name = "post_detail.html"


# Note: 'This mixin should be at the leftmost position in the inheritance list'.
class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    # default: template_name = "post_form.html"
    login_url = '/login/'
    redirect_field_name = 'blog/post_detail.html'  # where to go after create


class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    # default: template_name = "post_form.html"
    # default send object name: form
    login_url = '/login/'
    redirect_field_name = 'blog/post_detail.html'  # where to go after update


class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    # default: template_name = "post_confirm_delete.html"
    # default send object name to delete: object
    # that way it waits until actually deleting it , to give you back the success url
    success_url = reverse_lazy('post_list')  # where to go after delete


class DraftListView(LoginRequiredMixin, ListView):
    model = Post
    login_url = '/login/'
    redirect_field_name = 'blog/post_list.html'

    def get_queryset(self):
        return Post.objects.filter(published_date__isnull=True).order_by('create_date')


@login_required
def post_publish(request, pk):
    post = get_object_or_404(Post, pk=pk)
    post.publish()
    return redirect('post_detail', pk=pk)

######### Comments #####################################################################


@login_required
def add_comment_to_post(request, pk):
    # post = Post.objects.get(pk=pk)
    post = get_object_or_404(Post, pk=pk)

    if request.method == 'POST':
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.post = post
            comment.save()
            return redirect('post_detail', pk=pk)

    else:
        comment_form = CommentForm()
        return render(request, 'blog/comment_form.html', {'form': comment_form})


@login_required
def comment_approve(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    comment.approve()
    return redirect('post_detail', pk=comment.post.pk)


@login_required
def comment_remove(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    post_pk = comment.post.pk
    comment.delete()
    return redirect('post_detail', pk=post_pk)
