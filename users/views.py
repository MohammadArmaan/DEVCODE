from django.shortcuts import render, redirect, HttpResponse
from .models import Profile, Skill, Message
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CustomUserCreationForm, ProfileForm, SkillForm, MessageForm
from django.db.models import Q
from .utils import searchProfiles, paginateProfiles
from django.core.mail import send_mail
from django.conf import settings

# Create your views here.

def profiles(request):
    profiles, search_query = searchProfiles(request)
    coustom_range, profiles = paginateProfiles(request, profiles, 6)
    context={'profiles': profiles, 'search_query':search_query, 'coustom_range':coustom_range}
    return render(request,"users/profile.html", context)

def userProfile(request,pk):
    profile=Profile.objects.get(id=pk)
    topSkills=profile.skill_set.exclude(description__exact="")
    otherSkills=profile.skill_set.filter(description="")
    context={'profile':profile,'topSkills':topSkills,'otherSkills':otherSkills}
    return render(request, "users/user-profile.html",context)

def loginUser(request):
    page='register'
    if request.user.is_authenticated:
        return redirect("profiles")

    if request.method == "POST":
        username=request.POST['username']
        password=request.POST['password']

        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, "Username Does Not Exist!")
        user=authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.info(request, f"{user} has Logged in")

            return redirect(request.GET['next'] if 'next' in request.GET else 'account')
        else:
            messages.error(request, "Username/Password is Incorrect!")

    return render(request, "users/login_register.html")

def logoutUser(request):
    user = request.user
    logout(request)
    messages.info(request, f"{user} was logged Out!")
    return redirect('login')


def registerUser(request):
    page='register'
    form=CustomUserCreationForm()

    if request.method == "POST":
        form=CustomUserCreationForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            messages.success(request,"User Account was created")
            login(request,user)
            return redirect("edit-account")
        
        else:
            messages.error(request,"An Error has occured during registration")

    context={'page':page, 'form':form}
    return render(request, "users/login_register.html",context)


@login_required(login_url='login')
def userAccount(request):
    profile=request.user.profile
    topSkills=profile.skill_set.all()
    projects=profile.project_set.all()
    context={'profile': profile, 'topSkills':topSkills, 'projects':projects }
    return render(request, "users/account.html",context)

@login_required(login_url='login')
def editAccount(request):
    profile = request.user.profile
    form = ProfileForm(instance=profile)

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()

            return redirect('account')

    context = {'form': form}
    return render(request, 'users/profile_form.html', context)

@login_required(login_url="login")
def createSkill(request):
    profile=request.user.profile
    form=SkillForm()

    if request.method == 'POST':
        form=SkillForm(request.POST)

        if form.is_valid():
            skill=form.save(commit=False)
            skill.owner= profile
            skill.save()
            messages.success(request,"The Skill was Added Sucessfully!")
            return redirect('account')

    context={'form':form}
    return render(request, "users/skill-form.html",context)


@login_required(login_url="login")
def updateSkill(request,pk):
    profile=request.user.profile
    skill=profile.skill_set.get(id=pk)
    form=SkillForm(instance=skill)

    if request.method == 'POST':
        form=SkillForm(request.POST,instance=skill)

        if form.is_valid():
            skill.save()
            messages.success(request,"The Skill was Updated Sucessfully!")
            return redirect('account')

    context={'form':form}
    return render(request, "users/skill-form.html",context)

@login_required(login_url="login")
def deleteSkill(request,pk):
    profile=request.user.profile
    skill = profile.skill_set.get(id=pk)
    if request.method == 'POST':
        skill.delete()
        messages.success(request, "The Skill was Deleted Sucessfully!")
        return redirect('account')
    context={'object':skill}
    return render(request, "delete_template.html",context)

@login_required(login_url="login")
def inbox(request):
    profile=request.user.profile
    messageRequests = profile.messages.all()
    unreadCount = messageRequests.filter(is_read=False).count()
    context = {'messageRequests':messageRequests, 'unreadCount':unreadCount}
    return render(request, 'users/inbox.html', context)

@login_required(login_url="login")
def viewMessage(request,pk):

    profile = request.user.profile
    message = profile.messages.get(id=pk)
    if message.is_read == False:
        message.is_read = True
        message.save()
    context = {'message':message,}
    return render(request, 'users/message.html', context)


def createMessage(request,pk):
    recipient=Profile.objects.get(id=pk)
    mail=recipient.message_set.all()
    form = MessageForm()
    try:
        sender = request.user.profile
    except:
        sender = None
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message= form.save(commit=False)
            message.sender = sender
            message.recipient = recipient

            if sender:
                message.name = sender.name
                message.email = sender.email
            message.save()

            messages.success(request, "Your Message was Successfully Sent!")
            return redirect('user-profile',pk=recipient.id)

    context={'recipient':recipient, 'form':form}
    return render(request, "users/message_form.html", context)


