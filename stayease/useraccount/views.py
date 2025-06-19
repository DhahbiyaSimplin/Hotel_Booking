from django.shortcuts import render,redirect
from django.views.generic import View,TemplateView,ListView,DetailView,FormView
from .forms import LoginForm,RegForm
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from .models import Offer

# Create your views here.

class LandingView(View):
    def get(self,request):
        return render(request,"landing.html")
    

class HomeView(View):
    def get(self,request):
        offers = Offer.objects.all()
        return render(request, 'home.html', {'offers': offers})
    


class LoginView(FormView):
    template_name="login.html"
    form_class=LoginForm

    def post(self,request):
        form_data=LoginForm(data=request.POST)
        if form_data.is_valid():
            uname=form_data.cleaned_data.get ('username') 
            pswd=form_data.cleaned_data.get ('password')
            user=authenticate(request, username=uname, password=pswd)
            if user:
                login (request, user)
                messages. success(request, "Login Success!!")
                return redirect( 'user')
            else:
                messages. error (request, "Invalid Username or Password")
                return redirect( 'login')
        return render (request, "login.html", {"form":form_data})
    

class RegView(FormView):
    template_name="reg.html"
    form_class=RegForm

    def post(self, request):
        form_data=RegForm(data=request.POST)
        if form_data.is_valid():
            form_data.save()
            messages.success(request, "Registration Completed! !")
            return redirect( 'login')
        return render(request,"reg.html",{"form":form_data})
    

def logoutView(request):
    logout(request)
    messages.info(request,"Logged out successfully!")
    return redirect('login')

