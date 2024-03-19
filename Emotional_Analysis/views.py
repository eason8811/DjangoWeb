from django.shortcuts import render

def hello_world(request):
    is_login = request.user.is_authenticated
    return render(request, 'index.html', {'is_login': is_login})
