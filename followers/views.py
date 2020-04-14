from django.shortcuts import render


# Create your views here.
def new_user(request):
    if request.method == 'POST':
        data = request.POST.copy()
        name = data.get('name')
        print(data)
    else:
        name = '123'
    return render(request, 'followers/index.html', context={'name': name})
