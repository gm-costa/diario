from django.shortcuts import redirect, render
from django.urls import reverse
from django.contrib import messages
from django.db import transaction
from diario.models import Pessoa, Diario


def home(request):
    return render(request, 'home.html')

def escrever(request):
    template_name = 'escrever.html'
    pessoas = Pessoa.objects.all()
    context = {'pessoas': pessoas, 'tags': Diario.tags_choices}

    if request.method == "POST":
        titulo = request.POST.get('titulo')
        tags_selecionadas = request.POST.getlist('tags')
        pessoas_selecionadas = request.POST.getlist('pessoas')
        texto = request.POST.get('texto')
        print(tags_selecionadas)

        pessoas_selecionadas = [int(p) for p in pessoas_selecionadas]

        context['titulo'] = titulo
        context['tags_selecionadas'] = tags_selecionadas,
        context['pessoas_selecionadas'] = pessoas_selecionadas,
        context['texto'] = texto
        
        if not all((titulo, tags_selecionadas, pessoas_selecionadas, texto)):
            messages.add_message(request, messages.WARNING, 'Os campos são obrigatórios!')
            return render(request, template_name, context) 
        
        try:
            diario = Diario(
                titulo=titulo,
                texto=texto
            )
            diario.set_tags(tags_selecionadas)
            
            with transaction.atomic():
                diario.save()
                pessoa_objs = Pessoa.objects.filter(id__in=pessoas_selecionadas)
                diario.pessoas.add(*pessoa_objs)
                diario.save()
                messages.add_message(request, messages.SUCCESS, 'Diário publicado com sucesso.')
                return redirect(reverse('escrever'))
        except Exception as e:
            messages.add_message(request, messages.ERROR, f'Erro: {e}')
            return render(request, template_name, context)

    else:
        return render(request, template_name, context)

def cadastrar_pessoa(request):
    template_name = 'pessoa.html'
    if request.method == 'POST':
        nome = request.POST.get('nome')
        foto = request.FILES.get('foto')

        if not nome or not foto:
            messages.add_message(request, messages.WARNING, 'Os campos são obrigatórios!')
            return render(request, template_name, {'nome': nome})            

        try:
            pessoa = Pessoa(nome=nome, foto=foto)
            pessoa.save()
            messages.add_message(request, messages.SUCCESS, 'Cadastro realizado com sucesso.')
            return redirect(reverse('cadastrar_pessoa'))
        except Exception as e:
            messages.add_message(request, messages.ERROR, f'Erro: {e}')
            return render(request, template_name, {'nome': nome})
    
    else:
        return render(request, template_name)
