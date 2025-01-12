from datetime import datetime, timedelta
from django.shortcuts import redirect, render
from django.urls import reverse
from django.contrib import messages
from django.db import transaction
from django.db.models import Count
from diario.models import Pessoa, Diario


def home(request):
    escritas = Diario.objects.order_by('-create_at')
    ultimas_escritas = escritas[:3]

    # pessoas = Pessoa.objects.all()

    # nomes = [pessoa.nome for pessoa in pessoas]
    # qtds = []
    # for pessoa in pessoas:
    #     qtd = Diario.objects.filter(pessoas=pessoa).count()
    #     qtds.append(qtd)

    pessoas_com_contagem = Pessoa.objects.annotate(qtd_diarios=Count('diario'))
    nomes = [pessoa.nome for pessoa in pessoas_com_contagem]
    qtds = [pessoa.qtd_diarios for pessoa in pessoas_com_contagem]

    periodo = Diario.objects.filter(create_at__gte=datetime.now() - timedelta(days=6)).filter(create_at__lte=datetime.now())

    if periodo:
        periodo = periodo.values('create_at__date').annotate(qtd_escritas=Count('titulo'))

        dias_periodo = [datetime.strftime(x['create_at__date'], '%d/%m/%Y') for x in periodo]
        qtd_escritas = [x['qtd_escritas'] for x in periodo]

        for x in periodo:
            print(f"qtd_escritas: {x['qtd_escritas']} - criado em: {x['create_at__date']}")

    context = {
        'ultimas_escritas': ultimas_escritas, 
        'nomes': nomes, 
        'qtds': qtds,
        'dias_periodo': dias_periodo,
        'qtd_escritas': qtd_escritas
    }
    return render(request, 'home.html', context)

def escrever(request):
    template_name = 'escrever.html'
    pessoas = Pessoa.objects.all()
    context = {'pessoas': pessoas, 'tags': Diario.tags_choices}

    if request.method == "POST":
        titulo = request.POST.get('titulo')
        tags_selecionadas = request.POST.getlist('tags')
        pessoas_selecionadas = request.POST.getlist('pessoas')
        texto = request.POST.get('texto')

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

def dia(request):
    data = request.GET.get('data')
    data_formatada = datetime.strptime(data, '%Y-%m-%d')
    diarios = Diario.objects.filter(create_at__gte=data_formatada).filter(create_at__lte=data_formatada + timedelta(days=1))

    context = {'diarios': diarios, 'total': diarios.count(), 'data': data}

    return render(request, 'dia.html', context)

def excluir_dia(request):
    dia = datetime.strptime(request.GET.get('data'), '%Y-%m-%d')
    diarios = Diario.objects.filter(create_at__gte=dia).filter(create_at__lte=dia + timedelta(days=1))
    diarios.delete()
    return redirect(reverse('escrever'))

def excluir_escrita(request):
    link_anterior = request.META['HTTP_REFERER']
    escrita = int(request.GET.get('escrita'))
    diario = Diario.objects.filter(id=escrita)
    try:
        diario.delete()
        messages.add_message(request, messages.SUCCESS, 'Escrita removida com sucesso.')
    except Exception as e:
        messages.add_message(request, messages.ERROR, f'Erro: {e}')

    return redirect(link_anterior)
