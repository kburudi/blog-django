from django.shortcuts import render
from rest_framework import generics
from rest_framework.response import Response
from .models import BlogPost
from ..users.models import User, Profile
from .serializers import BlogPostSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated
from blog.backends import decode_token, is_owner
from cloudinary import uploader
from datetime import datetime
from django.utils.text import slugify
from django.shortcuts import get_object_or_404
import itertools


class CreateBlogPost(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = BlogPost.objects.all()
    serializer_class = BlogPostSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        token = request.auth.decode()
        user_id = decode_token(token)
        user = User.objects.get(id=user_id)
        profile = Profile.objects.get(user_id=user_id)
        user_name = profile.first_name+'_' + \
            '_'.join(profile.other_names.split())
        now = datetime.now().strftime("%Y%m%d_%H%M%S")
        image_url = ''

        try:
            image = request.FILES['image']
            image_ext = image.name.split('.')[-1]
            picture_name = user_name+'_'+now+'.'+image_ext
            image.name = picture_name
            cloudinary_response = uploader.upload(image)
            image_url = cloudinary_response['secure_url']
        except Exception:
            pass

        new_post = BlogPost()
        new_post.author = user
        new_post.title = serializer.data['title']
        new_post.content = serializer.data['content']
        new_post.image = image_url
        new_post.caption = serializer.data['caption']
        new_post.slug = orig = slugify(new_post.title)

        for x in itertools.count(1):
            if not BlogPost.objects.filter(slug=new_post.slug).exists():
                break
            new_post.slug = '%s-%d' % (orig, x)

        new_post.save()

        response_data = {
            'id': new_post.id,
            'slug': new_post.slug,
            'title': serializer.data['title'],
            'content': serializer.data['content'],
            'image': image_url,
            'caption': serializer.data['caption'],
            'author': user_id,
        }
        return Response(response_data, status=201)


class ListBlogPosts(generics.ListAPIView):
    serializer_class = BlogPostSerializer
    queryset = BlogPost.objects.all()


class RUDBlogPost(generics.RetrieveUpdateDestroyAPIView):
    permission_classes_by_action = {
        'retrieve': [AllowAny],
        'update': [IsAuthenticated],
        'destroy': [IsAuthenticated],
    }

    lookup_field = 'id'
    serializer_class = BlogPostSerializer
    queryset = BlogPost.objects.all()

    def update(self, request, id):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        token = request.auth.decode()
        user_id = decode_token(token)
        owner = is_owner(token, int(id))

        if owner:
            user = get_object_or_404(User, id=user_id)
            profile = Profile.objects.get(user_id=user_id)
            user_name = profile.first_name+'_' + \
                '_'.join(profile.other_names.split())

            now = datetime.now().strftime("%Y%m%d_%H%M%S")

            post = get_object_or_404(BlogPost, id=id)

            try:
                image = request.FILES['image']
                image_ext = image.name.split('.')[-1]
                picture_name = user_name+'_'+now+'.'+image_ext
                image.name = picture_name
                cloudinary_response = uploader.upload(image)
                post.image = cloudinary_response['secure_url']
            except Exception:
                pass

            if(serializer.data['caption'] is not None):
                post.caption = serializer.data['caption']

            post.title = serializer.data['title']
            post.content = serializer.data['content']
            post.save()

            response_data = {
                'title': post.title,
                'content': post.content,
                'image': post.image,
                'caption': post.caption,
                'author': user_id,
            }

            return Response(response_data, status=200)

        else:
            return Response({
                'message': "You cannot edit a post that is not yours"},
                status=403)

    def destroy(self, request, id):
        token = request.auth.decode()
        user_id = decode_token(token)
        owner = is_owner(token, int(id))

        if owner:
            post = BlogPost.objects.get(id=id)
            post.delete()

            return Response({
                'Message': "Blog Post was succesfully deleted"
            }, status=200)

        else:
            return Response({
                'message': "You cannot delete a post that is not yours"},
                status=403)
