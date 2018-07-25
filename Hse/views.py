from django.shortcuts import render
from django.conf import settings
import datetime
from datetime import date
from django.utils import timezone
from django.core.mail import EmailMessage
from django.core.mail import EmailMultiAlternatives
from django.shortcuts import redirect
from Hse.forms import chamado_hseForm, aux_tableForm, msgForm
from cadastro.models import empresa_terc, documento, funcionario, docs, docs_integracao, cad_resp
from usuario.models import Perfil
from Hse.models import chamado_hse, aux_table, logs, msg
from cadastro.forms import documentoForm, doc_Int_Form
from django.http import HttpResponseRedirect
from datetime import date, datetime, time, timedelta
from django.contrib.auth.models import User
from django.core import serializers
from django.http import Http404
from django.contrib.auth.decorators import permission_required
from mail_templated import send_mail
from mail_templated import EmailMessage
import base64
import os
from django.template.loader import render_to_string
from email.mime.image import MIMEImage
from Hse.lib import decodif, encoder




def hse(request):
	return render(request, 'hse.html')

def novo_chamado_hse(request):
    args = Perfil.objects.filter(user=request.user.username)
    print(args)
    if args.count() > 0:
        if request.method == 'POST':
            form = chamado_hseForm(request.POST)
            print (form.errors)
            if form.is_valid():
                post = form.save(commit=False)
                Emp = empresa_terc.objects.filter(id=post.empresa_id)[0]
                post.setor_solicitante = request.POST.get('setor_solicitante')
                post.gestor_solicitante = request.POST.get('gestor_solicitante')
                post.fone_solicitante = request.POST.get('fone_solicitante')
                post.status = 'Aguardando Terceiro'
                post.tempo_estimado = request.POST.get('tempo_estimado')
                print(request.POST.get('tempo_estimado'))
                post.email_terc = Emp.email
                post.solicitante = request.user
                post.email_solicitante = request.user.email
                post.save()
                print(post.id)
                obj= chamado_hse.objects.get(id = post.id)
                log = logs(num_cham=str(obj.id), ator=request.user.username, acao= "Abertura Chamado", tipo="open")
                log.id = None
                log.save()
                data = datetime.strptime(request.POST.get('tempo_estimado'), '%m/%d/%Y')
                dt = datetime.combine(data, time(00, 00)) - timedelta(days=4)
                arr = []
                dict = {}
                cont = 0
                for x in request.POST.getlist('tipo_servico'):
                    if x == '1':
                        arr.insert(cont,'Trabalho em alta tensão e eletricidade')
                        dict = {'CURSO DE ELETRICISTA':'Trabalho em alta tensão e eletricidade','ASO ALTA TENSÃO':'Trabalho em alta tensão e eletricidade','CURSO NR 10 OU RECICLAGEM':'Trabalho em alta tensão e eletricidade',}
                    if x == '2':
                        arr.insert(cont,'Trabalhos em altura')
                        cont = cont + 1            
                        dict.update({'CERTIFICADO TREINAMENTO NR35':'Trabalhos em altura','ASO TRABALHOS EM ALTURA':'Trabalhos em altura','FICHA DE EPI':'Trabalhos em altura',})
                    if x == '3':
                        arr.insert(cont,'Espaços confinados') 
                        cont = cont + 1           
                        dict.update({'CERTIFICADO TREINAMENTO DE VIGIA':'Espaços confinados','ASO ESPAÇO CONFINADO':'Espaços confinados','FICHA DE EPI':'Espaços confinados',})
                    if x == '4':
                        arr.insert(cont,'Operação de empilhadeira') 
                        cont = cont + 1           
                        dict.update({'ASO DA ADMISSÃO':'Operação de empilhadeira','CERTIFICADO OPERADOR EMPILHADEIRA':'Operação de empilhadeira',})
                    if x == '5':
                        arr.insert(cont,'Trabalhos com plataformas elevatórias')
                        cont = cont + 1
                        dict.update({'CURSO OPERADOR PLATAFORMA ELEVATÓRIA':'Trabalhos com plataformas elevatórias','ASO DA ADMISSÃO':'Trabalhos com plataformas elevatórias',})
                    if x == '6':
                        arr.insert(cont,'Operação de guindaste ou munck')
                        cont = cont + 1
                        dict.update({'CURSO DE GUINDASTE E/OU MUNCK':'Operação de guindaste ou munck','ASO DA ADMISSÃO':'Operação de guindaste ou munck','RINGGING PARA GUINDASTES':'Operação de guindaste ou munck',})
                    if x == '7':
                        arr.insert(cont,'Trabalhador autônomo - Firma individual')
                        cont = cont + 1
                        dict.update({'REGISTRO DA PREFEITURA':'Trabalhador autônomo - Firma individual','ASO':'Trabalhador autônomo - Firma individual','NÚMERO DE MATRÍCULA INSS':'Trabalhador autônomo - Firma individual',})
                    if x == '8':
                        arr.insert(cont,'Assistência Técnica - mautenção')
                        cont = cont + 1
                        dict.update({'CRACHÁ OU CARTEIRA PROFISSIONAL':'Assistência Técnica - mautenção','ASO':'Assistência Técnica - mautenção',})
                    if x == '9':
                        arr.insert(cont,'Soldador')
                        cont = cont + 1
                        dict.update({'PPRA DE SOLDA':'Soldador','COMPROVANTE DE CURSO OU EXPERIÊNCIA':'Soldador','FICHA DE EPI SOLDA':'Soldador',})
                qx = empresa_terc.objects.all()
                context = {
                    'solicitante': request.user.username,
                    'emp': Emp.nome_empresa,
                    'nome_proj': request.POST.get('nome_proj'),
                    'data_term': dt,
                    'obs': request.POST.get('descricao'),
                    'dict':dict,
                    'arr':arr,
                    'obj':obj,
                    'emp_id': post.empresa_id,
                    'qx': qx,
                    }
                message = EmailMessage('novo_chamEMAIL.html', context, settings.EMAIL_HOST_USER, [Emp.email,'eng_diego@live.com', 'gmartins86@gmail.com',], render=True )
                f = '/SIG_1.png'
                fp = open(os.path.join(os.path.dirname(__file__), f), 'rb')
                msg_img = MIMEImage(fp.read())
                fp.close()
                msg_img.add_header('Content-ID', '<{}>'.format(f))
                message.attach(msg_img)
                message.send()
                return redirect('show_cham_sol', "None")
        else:        
            form = chamado_hseForm()
        args = Perfil.objects.all()
        return render(request, 'novo_chamdo_hse.html', {'form': form, 'dado':args})
    else:
        return redirect('perfil')
        


def home_empresa(request):
	return render(request, 'home_empresa.html')


def show_cham_sol(request, nr):
    if nr == 'None':
        obj= chamado_hse.objects.filter(solicitante = request.user).latest('data_abertura')
    else:
        nu = decodif(nr)
        obj= chamado_hse.objects.get(id = nu)        
    arr = []
    dict = {}
    cont = 0
    for x in obj.tipo_servico:
        if x == '1':
            arr.insert(cont,'Trabalho em alta tensão e eletricidade')
            dict = {'CURSO DE ELETRICISTA':'Trabalho em alta tensão e eletricidade','ASO ALTA TENSÃO':'Trabalho em alta tensão e eletricidade','CURSO NR 10 OU RECICLAGEM':'Trabalho em alta tensão e eletricidade',}
        if x == '2':
            arr.insert(cont,'Trabalhos em altura')
            cont = cont + 1            
            dict.update({'CERTIFICADO TREINAMENTO NR35':'Trabalhos em altura','ASO TRABALHOS EM ALTURA':'Trabalhos em altura','FICHA DE EPI':'Trabalhos em altura',})
        if x == '3':
            arr.insert(cont,'Espaços confinados') 
            cont = cont + 1           
            dict.update({'CERTIFICADO TREINAMENTO DE VIGIA':'Espaços confinados','ASO ESPAÇO CONFINADO':'Espaços confinados','FICHA DE EPI':'Espaços confinados',})
        if x == '4':
            arr.insert(cont,'Operação de empilhadeira') 
            cont = cont + 1           
            dict.update({'ASO DA ADMISSÃO':'Operação de empilhadeira','CERTIFICADO OPERADOR EMPILHADEIRA':'Operação de empilhadeira',})
        if x == '5':
            arr.insert(cont,'Trabalhos com plataformas elevatórias')
            cont = cont + 1
            dict.update({'CURSO OPERADOR PLATAFORMA ELEVATÓRIA':'Trabalhos com plataformas elevatórias','ASO DA ADMISSÃO':'Trabalhos com plataformas elevatórias',})
        if x == '6':
            arr.insert(cont,'Operação de guindaste ou munck')
            cont = cont + 1
            dict.update({'CURSO DE GUINDASTE E/OU MUNCK':'Operação de guindaste ou munck','ASO DA ADMISSÃO':'Operação de guindaste ou munck','RINGGING PARA GUINDASTES':'Operação de guindaste ou munck',})
        if x == '7':
            arr.insert(cont,'Trabalhador autônomo - Firma individual')
            cont = cont + 1
            dict.update({'REGISTRO DA PREFEITURA':'Trabalhador autônomo - Firma individual','ASO':'Trabalhador autônomo - Firma individual','NÚMERO DE MATRÍCULA INSS':'Trabalhador autônomo - Firma individual',})
        if x == '8':
            arr.insert(cont,'Assistência Técnica - mautenção')
            cont = cont + 1
            dict.update({'CRACHÁ OU CARTEIRA PROFISSIONAL':'Assistência Técnica - mautenção','ASO':'Assistência Técnica - mautenção',})
        if x == '9':
            arr.insert(cont,'Soldador')
            cont = cont + 1
            dict.update({'PPRA DE SOLDA':'Soldador','COMPROVANTE DE CURSO OU EXPERIÊNCIA':'Soldador','FICHA DE EPI SOLDA':'Soldador',})
    emp = empresa_terc.objects.all()
    N_CHM = '%0*d' % (5, obj.id)
    mycham= chamado_hse.objects.filter(solicitante = request.user)
    data = datetime.strptime(obj.tempo_estimado, '%m/%d/%Y')
    dt = datetime.combine(data, time(00, 00)) - timedelta(days=4)
    minus4 = dt.date() - timedelta(days=4) 
    minus6 = dt.date() - timedelta(days=6)  
    d1 = datetime.strptime(timezone.localtime().strftime('%Y-%m-%d'), "%Y-%m-%d").date()
    d2 = datetime.strptime(minus6.strftime('%Y-%m-%d'), "%Y-%m-%d").date()
    rest = (d2 - d1).days
    if rest > 0:
         rest = "RESTAM   " + str(abs((d1 - d2).days))
    else:
        rest = "ATRASADO !   " + str(abs((d1 - d2).days))
    print(minus6)
    obj.data  = minus6
    obj.save()
    colab = aux_table.objects.filter(num_cham = obj.id)
    msgs = msg.objects.filter(num_cham = obj.id)
    log = logs.objects.filter(num_cham = obj.id)
    #Us = User.objects.get(username=obj.gestor_solicitante)'Em_g':Us.email,
    resp = cad_resp.objects.all()
    return render(request, 'show_cham_sol.html', {'resp':resp, 'd1':d1,  'dw':data.date(), 'log':log,'msgs':msgs,'colab':colab,'obj':obj,'N_CHM':N_CHM,'emp':emp,'mycham':mycham,'minus4':minus4,'minus6':minus6,'rest':rest,'arr':arr,'dict':dict})

def show_my_cham(request, num_chamG, idG):
    if num_chamG == "None":
        try:
            obj= chamado_hse.objects.all().latest('data_abertura')
        except chamado_hse.DoesNotExist:
            raise Http404("Nenhum Chamado Existente para sua Empresa.")
    else:
        num_cham = decodif(num_chamG)
        obj= chamado_hse.objects.get(id = num_cham)
    id = decodif(idG)
    arr = []
    dict = {}
    cont = 0
    for x in obj.tipo_servico:
        if x == '1':
            arr.insert(cont,'Trabalho em alta tensão e eletricidade')
            dict = {'CURSO DE ELETRICISTA':'Trabalho em alta tensão e eletricidade','ASO ALTA TENSÃO':'Trabalho em alta tensão e eletricidade','CURSO NR 10 OU RECICLAGEM':'Trabalho em alta tensão e eletricidade',}
        if x == '2':
            arr.insert(cont,'Trabalhos em altura')
            cont = cont + 1            
            dict.update({'CERTIFICADO TREINAMENTO NR35':'Trabalhos em altura','ASO TRABALHOS EM ALTURA':'Trabalhos em altura','FICHA DE EPI':'Trabalhos em altura',})
        if x == '3':
            arr.insert(cont,'Espaços confinados') 
            cont = cont + 1           
            dict.update({'CERTIFICADO TREINAMENTO DE VIGIA':'Espaços confinados','ASO ESPAÇO CONFINADO':'Espaços confinados','FICHA DE EPI':'Espaços confinados',})
        if x == '4':
            arr.insert(cont,'Operação de empilhadeira') 
            cont = cont + 1           
            dict.update({'ASO DA ADMISSÃO':'Operação de empilhadeira','CERTIFICADO OPERADOR EMPILHADEIRA':'Operação de empilhadeira',})
        if x == '5':
            arr.insert(cont,'Trabalhos com plataformas elevatórias')
            cont = cont + 1
            dict.update({'CURSO OPERADOR PLATAFORMA ELEVATÓRIA':'Trabalhos com plataformas elevatórias','ASO DA ADMISSÃO':'Trabalhos com plataformas elevatórias',})
        if x == '6':
            arr.insert(cont,'Operação de guindaste ou munck')
            cont = cont + 1
            dict.update({'CURSO DE GUINDASTE E/OU MUNCK':'Operação de guindaste ou munck','ASO DA ADMISSÃO':'Operação de guindaste ou munck','RINGGING PARA GUINDASTES':'Operação de guindaste ou munck',})
        if x == '7':
            arr.insert(cont,'Trabalhador autônomo - Firma individual')
            cont = cont + 1
            dict.update({'REGISTRO DA PREFEITURA':'Trabalhador autônomo - Firma individual','ASO':'Trabalhador autônomo - Firma individual','NÚMERO DE MATRÍCULA INSS':'Trabalhador autônomo - Firma individual',})
        if x == '8':
            arr.insert(cont,'Assistência Técnica - mautenção')
            cont = cont + 1
            dict.update({'CRACHÁ OU CARTEIRA PROFISSIONAL':'Assistência Técnica - mautenção','ASO':'Assistência Técnica - mautenção',})
        if x == '9':
            arr.insert(cont,'Soldador')
            cont = cont + 1
            dict.update({'PPRA DE SOLDA':'Soldador','COMPROVANTE DE CURSO OU EXPERIÊNCIA':'Soldador','FICHA DE EPI SOLDA':'Soldador',})
    emp = empresa_terc.objects.all()
    N_CHM = '%0*d' % (5, obj.id)
    mycham= chamado_hse.objects.filter(empresa_id = id)
    data = datetime.strptime(obj.tempo_estimado, '%m/%d/%Y')
    dt = datetime.combine(data, time(00, 00)) - timedelta(days=4)
    minus4 = dt.date() - timedelta(days=4) 
    minus6 = dt.date() - timedelta(days=6)  
    d1 = datetime.strptime(timezone.localtime().strftime('%Y-%m-%d'), "%Y-%m-%d").date()
    d2 = datetime.strptime(minus6.strftime('%Y-%m-%d'), "%Y-%m-%d").date()
    rest = (d2 - d1).days
    if rest > 0:
         rest = "RESTAM   " + str(abs((d1 - d2).days))
    else:
        rest = "ATRASADO !   " + str(abs((d1 - d2).days))
    print(minus6)
    obj.data  = minus6
    obj.save()
    fun = funcionario.objects.filter(empresa_id = id)
    dc = chamado_hse.objects.filter(empresa_id = id)
    colab = aux_table.objects.filter(num_cham = obj.id)
    log = logs.objects.filter(num_cham = obj.id)
    msgs = msg.objects.filter(num_cham = obj.id)
    func = funcionario.objects.filter(empresa_id=id)
    print(data.date())
    #Us = User.objects.get(username=obj.gestor_solicitante)'Em_g':Us.email,
    respo = cad_resp.objects.filter(empresa_resp=id)
    return render(request, 'chamados.html', {'respo':respo, 'dw':data.date(), 'func':func, 'msgs':msgs,'log':log,'colab':colab,'id':id,'fun':fun,'obj':obj,'N_CHM':N_CHM,'emp':emp,'mycham':mycham,'minus4':minus4,'minus6':minus6,'rest':rest,'arr':arr,'dict':dict})


def meus_chamados(request):
    mycham= chamado_hse.objects.filter(solicitante = request.user)
    emp  = empresa_terc.objects.all()
    return render(request, 'meus_chamados.html', {'mycham':mycham, 'emp':emp})

def include_col(request, id, num):
    lm = request.POST.get('num_cham') #recebe o número do chamado
    fun = request.POST.getlist('colab[]') # recebe os colaboradores selecionados
    key = request.POST.get('tps')#recebe o tipo de serviço relacionado
    arr1 = []
    try:
        data = aux_table.objects.filter(num_cham = lm, tps = key)
    except:
        data = None
    if data:
        for rec in data:
            rec.delete()
        cont = 0
        num_cham = lm
        for fb in fun:
            x = fb
            a,b = x.split(",")
            arr1.append(a)
            action = ""
            aux = (a +";")
            action = action  + aux
            form = aux_tableForm(request.POST)
            print (form.errors)
            if form.is_valid():
                post = form.save(commit=False)
                post.colab = a
                post.id_col = b
                post.save()
                y =  action 
        log = logs(num_cham=str(lm), ator=request.user.username, acao= str(arr1), tipo="add_col")
        log.id = None
        log.save()
        ab = encoder(str(num_cham))
        cb = encoder(str(id))
        print(ab)
        print(cb)
        return redirect('show_my_cham', ab, cb)
    else:
        num_cham = lm
        for fb in fun:
            x = fb
            a,b = x.split(",")
            arr1.append(a)
            form = aux_tableForm(request.POST)
            print (form.errors)
            print("adding:"+a+", with id:"+b)
            if form.is_valid():
                post = form.save(commit=False)
                post.colab = a
                post.id_col = b
                post.save()
        log = logs(num_cham=str(lm), ator=request.user.username, acao= str(arr1), tipo="add_col")
        log.id = None
        log.save()
        ab = encoder(str(num_cham))
        cb = encoder(str(id))
        print(ab)
        print(cb)
        return redirect('show_my_cham', ab, cb)              

def cad_docs(request):
    if request.method == 'POST':
        form = docsF(request.POST)
        print (form.errors)
        if form.is_valid():
            post = form.save(commit=False)
            
            post.save()
            return redirect('cad_docs')
    else:        
        form = docsF()
    return render(request, 'cad_docs.html', {'form': form})



def message(request, id, num):
    if request.method == 'POST':
        form = msgForm(request.POST)
        print (form.errors)
        if form.is_valid():
            post = form.save(commit=False)
            post.data = timezone.now()
            post.ator = request.user.username
            post.save()
            log = logs(num_cham=str(num), ator=request.user.username, acao= request.POST.get("msg"), tipo="msg")
            log.id = None
            log.save()
            aux1 = encoder(str(num))
            aux2 = encoder(str(id))
            return redirect('show_my_cham', aux1, aux2)
    else:        
        form = msgForm()
        aux1 = encoder(str(num))
        aux2 = encoder(str(id))
    return redirect('show_my_cham', aux1, aux2)

def message_sol(request, num, orig):
    if request.method == 'POST':
        form = msgForm(request.POST)
        bas = request.POST.getlist('ema[]')
        bas = list(set(bas))
        for hn in bas:
            print(hn)
        print (form.errors)
        if form.is_valid():
            post = form.save(commit=False)
            post.data = timezone.now()
            if request.POST.get('fun'):
                post.id_col = request.POST.get('fun')
                post.tipo = "lib"
            else:
                post.id_col = "123"
                post.tipo = "123"                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           
            post.ator = request.user.username
            post.save()
            log = logs(num_cham=str(num), ator=request.user.username, acao= request.POST.get("msg"), tipo="msg")
            log.id = None
            log.save()
            if orig == "f_terc":
                pass
            else:
                obj = chamado_hse.objects.get(id=num)
            emp = empresa_terc.objects.all()
            if bas:
                context = {
                        'solicitante': request.user.username,
                        'emp': 'qwedsa',
                        'nome_proj': request.POST.get('nome_proj'),
                        'msg': request.POST.get("msg"),
                        'num': num,
                        'obj':obj,
                        'emp':emp,
                        }
                message = EmailMessage('MSG_EMAIL.html', context, settings.EMAIL_HOST_USER, bas, render=True )
                f = '/SIG_1.png'
                fp = open(os.path.join(os.path.dirname(__file__), f), 'rb')
                msg_img = MIMEImage(fp.read())
                fp.close()
                msg_img.add_header('Content-ID', '<{}>'.format(f))
                message.attach(msg_img)
                message.send() 
            if orig == "ter":
                aux1 = encoder(str(num))
                aux2 = encoder(request.POST.get('emp'))
                return redirect('show_my_cham', aux1, aux2)
            elif orig == "sol":
                aux1 = encoder(str(num))
                return redirect('show_cham_sol', aux1)
            elif orig == "f_terc":
                aux1 = encoder(request.POST.get('fun'))
                aux2 = encoder(request.POST.get('empresa'))
                return redirect('documentacao', aux1, aux2)
    else:        
        form = msgForm()
        aux1 = encoder(str(num))
    return redirect('show_cham_sol', aux1)

def message_hse(request, id, num):
    if request.method == 'POST':
        form = msgForm(request.POST)
        print (form.errors)
        if form.is_valid():
            post = form.save(commit=False)
            post.data = timezone.now()
            post.tipo = "123"
            post.id_col = "123"
            post.ator = request.user.username
            post.save()
            log = logs(num_cham=str(num), ator=request.user.username, acao= request.POST.get("msg"), tipo="msg")
            log.id = None
            log.save()
            aux1 = encoder(str(num))
            aux2 = encoder(str(id))
            return redirect('view_cham_hse', aux1, aux2)
    else:        
        form = msgForm()
        aux1 = encoder(str(num))
        aux2 = encoder(str(id))
    return redirect('view_cham_hse', aux1, aux2)



@permission_required('Hse.add_hse', login_url="/hse/")
def gestao(request):
    mycham= chamado_hse.objects.all()
    emp = empresa_terc.objects.all()
    fun = funcionario.objects.all()
    return render(request, 'gestão.html', {'fun':fun, 'mycham':mycham, 'emp':emp})


                       
# TODO: Add more useful commands here.



def view_cham_hse(request, numG, idG):
    num = decodif(numG)
    id = decodif(idG)
    obj= chamado_hse.objects.get(id = num)
    arr = []
    dict = {}
    cont = 0
    for x in obj.tipo_servico:
        if x == '1':
            arr.insert(cont,'Trabalho em alta tensão e eletricidade')
            dict = {'CURSO DE ELETRICISTA':'Trabalho em alta tensão e eletricidade','ASO ALTA TENSÃO':'Trabalho em alta tensão e eletricidade','CURSO NR 10 OU RECICLAGEM':'Trabalho em alta tensão e eletricidade',}
        if x == '2':
            arr.insert(cont,'Trabalhos em altura')
            cont = cont + 1            
            dict.update({'CERTIFICADO TREINAMENTO NR35':'Trabalhos em altura','ASO TRABALHOS EM ALTURA':'Trabalhos em altura','FICHA DE EPI':'Trabalhos em altura',})
        if x == '3':
            arr.insert(cont,'Espaços confinados') 
            cont = cont + 1           
            dict.update({'CERTIFICADO TREINAMENTO DE VIGIA':'Espaços confinados','ASO ESPAÇO CONFINADO':'Espaços confinados','FICHA DE EPI':'Espaços confinados',})
        if x == '4':
            arr.insert(cont,'Operação de empilhadeira') 
            cont = cont + 1           
            dict.update({'ASO DA ADMISSÃO':'Operação de empilhadeira','CERTIFICADO OPERADOR EMPILHADEIRA':'Operação de empilhadeira',})
        if x == '5':
            arr.insert(cont,'Trabalhos com plataformas elevatórias')
            cont = cont + 1
            dict.update({'CURSO OPERADOR PLATAFORMA ELEVATÓRIA':'Trabalhos com plataformas elevatórias','ASO DA ADMISSÃO':'Trabalhos com plataformas elevatórias',})
        if x == '6':
            arr.insert(cont,'Operação de guindaste ou munck')
            cont = cont + 1
            dict.update({'CURSO DE GUINDASTE E/OU MUNCK':'Operação de guindaste ou munck','ASO DA ADMISSÃO':'Operação de guindaste ou munck','RINGGING PARA GUINDASTES':'Operação de guindaste ou munck',})
        if x == '7':
            arr.insert(cont,'Trabalhador autônomo - Firma individual')
            cont = cont + 1
            dict.update({'REGISTRO DA PREFEITURA':'Trabalhador autônomo - Firma individual','ASO AUTONOMO':'Trabalhador autônomo - Firma individual','NÚMERO DE MATRÍCULA INSS':'Trabalhador autônomo - Firma individual',})
        if x == '8':
            arr.insert(cont,'Assistência Técnica - mautenção')
            cont = cont + 1
            dict.update({'CRACHÁ OU CARTEIRA PROFISSIONAL':'Assistência Técnica - mautenção','ASO ASSIST. TÉCNICA':'Assistência Técnica - mautenção',})
        if x == '9':
            arr.insert(cont,'Soldador')
            cont = cont + 1
            dict.update({'PPRA DE SOLDA':'Soldador','COMPROVANTE DE CURSO OU EXPERIÊNCIA':'Soldador','FICHA DE EPI SOLDA':'Soldador',})
    emp = empresa_terc.objects.all()
    N_CHM = '%0*d' % (5, obj.id)
    mycham= chamado_hse.objects.filter(solicitante = request.user)
    data = datetime.strptime(obj.tempo_estimado, '%m/%d/%Y')
    dt = datetime.combine(data, time(00, 00)) - timedelta(days=4)
    minus4 = dt.date() - timedelta(days=4) 
    minus6 = dt.date() - timedelta(days=6)  
    d1 = datetime.strptime(timezone.localtime().strftime('%Y-%m-%d'), "%Y-%m-%d").date()
    d2 = datetime.strptime(minus6.strftime('%Y-%m-%d'), "%Y-%m-%d").date()
    rest = abs((d1 - d2).days)
    colab = aux_table.objects.filter(num_cham = obj.id)
    func = funcionario.objects.filter(empresa_id=id)
    msgs = msg.objects.filter(num_cham = obj.id)
    log = logs.objects.filter(num_cham = obj.id)
    resp = cad_resp.objects.filter(empresa_resp=id)
    return render(request, 'view_cham_hse.html', {'resp':resp, 'dw':data.date(), 'func':func, 'log':log,'msgs':msgs,'colab':colab,'obj':obj,'N_CHM':N_CHM,'emp':emp,'mycham':mycham,'minus4':minus4,'minus6':minus6,'rest':rest,'arr':arr,'dict':dict,'id':id})


def documentosHse(request, idG):
    id = decodif(idG)
    fun = funcionario.objects.get(id=id)
    a_docs = docs.objects.filter(tipo = "B").values_list('nome', flat=True)
    c_docs = docs.objects.filter(tipo = "C").values_list('nome', flat=True)
    b_docs = docs.objects.all()
    aux = documento.objects.filter(funcionario = id)
    msgs = msg.objects.filter(tipo="lib", id_col=id)
    arr = []
    dict = {}
    for dc in a_docs:
        arr.append(dc)
    i = 0
    cont = 0
    while i < len(arr):
        key = arr[i]
        dict.setdefault(key, [])
        for fb in aux:
            if fb.nome_documento == arr[i]:
                cont = cont + 1
                dict[key].append(fb.arquivo_documento)
        cont = 0
        i += 1
    arr1 = []
    dict1 = {}
    for dc in c_docs:
        arr1.append(dc)
    i = 0
    cont = 0
    while i < len(arr1):
        key = arr1[i]
        dict1.setdefault(key, [])
        for fb in aux:
            if fb.nome_documento == arr1[i]:
                cont = cont + 1
                dict1[key].append(fb.arquivo_documento)
        cont = 0
        i += 1
    try:
        el = docs_integracao.objects.get(funcionario=id)
    except:
        el = None
    return render(request, 'documentação1.html',{'fun_data':fun.data_int, 'el':el, 'msgs':msgs, 'fun':fun ,'arr': arr, 'dict': dict,'dict1': dict1, 'docs': b_docs, 'aux': aux,'id': id })


def saveCham(request, num, id):
    mycham= chamado_hse.objects.get(id=num)
    mycham.status = request.POST.get('gr')
    mycham.save()
    emp = empresa_terc.objects.all()
    docs = documento.objects.filter(hse=1)
    subject, from_email, to = 'Alteração no Chamado'+str(id)+', - Hse', settings.EMAIL_HOST_USER, 'eng_diego@live.com'
    text_content = 'texto de chamados.'
    html_content = ' <head><meta name="viewport" content="width=device-width, initial-scale=1.0" /><meta http-equiv="Content-Type" content="text/html; charset=UTF-8" /><style type="text/css" rel="stylesheet" media="all">body{width:100%!important;height:100%;margin:0;line-height:1.4;background-color:#F2F4F6;color:#74787E;-webkit-text-size-adjust:none}body{width:100%!important;height:100%;margin:0;line-height:1.4;background-color:#F2F4F6;color:#74787E;-webkit-text-size-adjust:none}.email-wrapper{width:100%;margin:0;padding:0;background-color:#F2F4F6}.email-content{width:100%;margin:0;padding:0}.email-masthead{padding:25px0;text-align:center}.email-masthead_logo{max-width:400px;border:0}.email-masthead_name{font-size:16px;font-weight:bold;color:#2F3133;text-decoration:none;text-shadow:01px0white}.email-logo{max-height:50px}.email-body{width:100%;margin:0;padding:0;border-top:1pxsolid#EDEFF2;border-bottom:1pxsolid#EDEFF2;background-color:#FFF}.email-body_inner{width:570px;margin:0auto;padding:0}.email-footer{width:570px;margin:0auto;padding:0;text-align:center}.email-footerp{color:#AEAEAE}.body-action{width:100%;margin:30pxauto;padding:0;text-align:center}.body-dictionary{width:100%;overflow:hidden;margin:20pxauto10px;padding:0}.body-dictionarydd{margin:0010px0}.body-dictionarydt{clear:both;color:#000;font-weight:bold}.body-dictionarydd{margin-left:0;margin-bottom:10px}.body-sub{margin-top:25px;padding-top:25px;border-top:1pxsolid#EDEFF2;table-layout:fixed}.body-suba{word-break:break-all}.content-cell{padding:35px;background-image:linear-gradient( rgba(255,255,255,.7) 0%,rgba(255,255,255,.7) 100%),url("")}.align-right{text-align:right}h1{margin-top:0;color:#2F3133;font-size:19px;font-weight:bold}h2{margin-top:0;color:#2F3133;font-size:16px;font-weight:bold}h3{margin-top:0;color:#2F3133;font-size:14px;font-weight:bold}blockquote{margin:1.7rem0;padding-left:0.85rem;border-left:10pxsolid#F0F2F4}blockquotep{font-size:1.1rem;color:#999}blockquotecite{display:block;text-align:right;color:#666;font-size:1.2rem}cite{display:block;font-size:0.925rem}cite:before{content:"2014020"}p{margin-top:0;color:#74787E;font-size:16px;line-height:1.5em}p.sub{font-size:12px}p.center{text-align:center}table{width:100%}th{padding:0px5px;padding-bottom:8px;border-bottom:1pxsolid#EDEFF2}thp{margin:0;color:#9BA2AB;font-size:12px}td{padding:10px5px;color:#74787E;font-size:15px;line-height:18px}.content{align:center;padding:0}.data-wrapper{width:100%;margin:0;padding:35px0}.data-table{width:100%;margin:0}.data-tableth{text-align:left;padding:0px5px;padding-bottom:8px;border-bottom:1pxsolid#EDEFF2}.data-tablethp{margin:0;color:#9BA2AB;font-size:12px}.data-tabletd{padding:10px5px;color:#74787E;font-size:15px;line-height:18px}.button{display:inline-block;width:200px;background-color:#3869D4;border-radius:3px;color:#fff;font-size:15px;line-height:45px;text-align:center;text-decoration:none;-webkit-text-size-adjust:none;mso-hide:all}@mediaonlyscreenand(max-width:600px){.email-body_inner,.email-footer{width:100%!important}}@mediaonlyscreenand(max-width:500px){.button{width:100%!important}}</style><style type="text/css">.tg{border-collapse:collapse;border-spacing:0}.tg td{font-family:Arial,sans-serif;font-size:14px;padding:10px 5px;border-style:solid;border-width:1px;overflow:hidden;word-break:normal;border-color:black}.tg th{font-family:Arial,sans-serif;font-size:14px;font-weight:normal;padding:10px 5px;border-style:solid;border-width:1px;overflow:hidden;word-break:normal;border-color:black}.tg .tg-t1lb{font-family:"Courier New",Courier,monospace!important;border-color:inherit;vertical-align:top}.tg .tg-gc4a{font-family:"Courier New",Courier,monospace!important;border-color:inherit;text-align:center}.tg .tg-ji20{font-family:"Courier New",Courier,monospace!important;border-color:inherit}</style></head><body dir="ltr"><table class="email-wrapper" width="100%" cellpadding="0" cellspacing="0"><tr><td class="content"><table class="email-content" width="100%" cellpadding="0" cellspacing="0"><tr><td class="email-masthead"><a class="email-masthead_name" href="https://example-hermes.com/" target="_blank"><img src="https://uploaddeimagens.com.br/images/001/404/729/original/SIG_1.png?1525586751" class="email-logo" /></a></td></tr><tr><td class="email-body" width="100%"><table class="email-body_inner" align="center" width="570" cellpadding="0" cellspacing="0"><tr><td class="content-cell"><h1>Olá ' +"NOME"+ ',</h1><p class style="text-align:justify;">A <strong>SIG COMBIBLOC </strong>solicitou o envio dos documentos requisitados referentes á execução do Projeto: ######## abaixo bem como a continuidade do processo que deve ser concuído até ##/##/####. Evite atrasos, na devida liberação de acesso do pessoal que irá realizar as atividades solicitadas, todas as documentações exigidas deverão ser entreges conforme previsto.<br><strong>Solicitante :</strong>Diego do Nascimento<br><strong>Obs :</strong>   Olá, conforme combinamos anteriormente, estou formalizando o processo de juntar as documentações referentes aos serviços que serão executados no projeto AMPLIAÇÃO BLOCO 3.<br> att, <br>Diego do Nascimento.</p><table class="tg"><tr><th class="tg-gc4a" rowspan="4">Solicitado: <span style="font-weight:bold;font-style:italic;color:rgb(254, 0, 0)">Trabalho em Altura</span><span style="font-style:italic;color:rgb(254, 0, 0)"> </span></th><th class="tg-3ib7"> Documentações Solicitadas</th></tr><tr><td class="tg-ji20">Cópia do treinamento NR 35<br>Duração mínima 8 horas</td></tr><tr><td class="tg-t1lb">Cópia ASO que deve contar eletroecefalograma<br>com especificação "Apto para trabalhar em altura"</td></tr><tr><td class="tg-t1lb">Ficha de EPI que evidenciar recebimento do cinto<br>de segurança com duplo balabarte, capacete e <br>respectivos CAs</td></tr></table><hr /><p>Em caso de dúvidas entre em contato por: <a href="mailto:mail_HSE@gmail.com">mail_HSE@gmail.com</a> ou pelos telefones: (41)XXXX-XXXX  ; (41)XXXX-XXXX</p><p>Best Regards / Atenciosamente,<br /> Setor HSE-Sig Combibloc</p></td></tr></table></td></tr><tr><td><table class="email-footer" align="center" width="570" cellpadding="0" cellspacing="0"><tr><td class="content-cell"><p class="sub center" style="color:blue"> <strong><h2>SIG Combibloc do Brasil Ltda.</h2></strong><p style="color:blue">Rodovia BR 277 - 120,4 KM</p><p style="color:blue">83605-590 - Campo Largo - Paraná / Brasil</p></p></td></tr></table></td></tr></table></td></tr></table>'
    msg = EmailMultiAlternatives(subject, text_content, from_email, ['eng_diego@live.com',mycham.email_terc])
    msg.attach_alternative(html_content, "text/html")
    msg.send()
    gth = encoder(num)
    hhy = encoder(id)
    return redirect('view_cham_hse', gth, hhy)

def action(request, id):
    if request.POST.get('buton') == 'submeter':
        fun = funcionario.objects.get(id=id)
        fun.status = request.POST.get('lib')
        fun.save()
        m1 = msg(num_cham=00, ator=request.user.username, msg=request.POST.get('messa'), tipo="lib", id_col=id)
        m1.id = None
        m1.save()
        #subject, from_email, to = 'Solicitação da Sig Combibloc para a '+ Contato, settings.EMAIL_HOST_USER, 'to@example.com'
        #text_content = 'This is an important message.'
        #html_content = '<head><meta name="viewport" content="width=device-width, initial-scale=1.0" /><meta http-equiv="Content-Type" content="text/html; charset=UTF-8" /><style type="text/css" rel="stylesheet" media="all">body{width:100%!important;height:100%;margin:0;line-height:1.4;background-color:#F2F4F6;color:#74787E;-webkit-text-size-adjust:none}body{width:100%!important;height:100%;margin:0;line-height:1.4;background-color:#F2F4F6;color:#74787E;-webkit-text-size-adjust:none}.email-wrapper{width:100%;margin:0;padding:0;background-color:#F2F4F6}.email-content{width:100%;margin:0;padding:0}.email-masthead{padding:25px0;text-align:center}.email-masthead_logo{max-width:400px;border:0}.email-masthead_name{font-size:16px;font-weight:bold;color:#2F3133;text-decoration:none;text-shadow:01px0white}.email-logo{max-height:50px}.email-body{width:100%;margin:0;padding:0;border-top:1pxsolid#EDEFF2;border-bottom:1pxsolid#EDEFF2;background-color:#FFF}.email-body_inner{width:570px;margin:0auto;padding:0}.email-footer{width:570px;margin:0auto;padding:0;text-align:center}.email-footerp{color:#AEAEAE}.body-action{width:100%;margin:30pxauto;padding:0;text-align:center}.body-dictionary{width:100%;overflow:hidden;margin:20pxauto10px;padding:0}.body-dictionarydd{margin:0010px0}.body-dictionarydt{clear:both;color:#000;font-weight:bold}.body-dictionarydd{margin-left:0;margin-bottom:10px}.body-sub{margin-top:25px;padding-top:25px;border-top:1pxsolid#EDEFF2;table-layout:fixed}.body-suba{word-break:break-all}.content-cell{padding:35px;background-image:linear-gradient( rgba(255,255,255,.7) 0%,rgba(255,255,255,.7) 100%),url("")}.align-right{text-align:right}h1{margin-top:0;color:#2F3133;font-size:19px;font-weight:bold}h2{margin-top:0;color:#2F3133;font-size:16px;font-weight:bold}h3{margin-top:0;color:#2F3133;font-size:14px;font-weight:bold}blockquote{margin:1.7rem0;padding-left:0.85rem;border-left:10pxsolid#F0F2F4}blockquotep{font-size:1.1rem;color:#999}blockquotecite{display:block;text-align:right;color:#666;font-size:1.2rem}cite{display:block;font-size:0.925rem}cite:before{content:"2014020"}p{margin-top:0;color:#74787E;font-size:16px;line-height:1.5em}p.sub{font-size:12px}p.center{text-align:center}table{width:100%}th{padding:0px5px;padding-bottom:8px;border-bottom:1pxsolid#EDEFF2}thp{margin:0;color:#9BA2AB;font-size:12px}td{padding:10px5px;color:#74787E;font-size:15px;line-height:18px}.content{align:center;padding:0}.data-wrapper{width:100%;margin:0;padding:35px0}.data-table{width:100%;margin:0}.data-tableth{text-align:left;padding:0px5px;padding-bottom:8px;border-bottom:1pxsolid#EDEFF2}.data-tablethp{margin:0;color:#9BA2AB;font-size:12px}.data-tabletd{padding:10px5px;color:#74787E;font-size:15px;line-height:18px}.button{display:inline-block;width:200px;background-color:#3869D4;border-radius:3px;color:#fff;font-size:15px;line-height:45px;text-align:center;text-decoration:none;-webkit-text-size-adjust:none;mso-hide:all}@mediaonlyscreenand(max-width:600px){.email-body_inner,.email-footer{width:100%!important}}@mediaonlyscreenand(max-width:500px){.button{width:100%!important}}</style></head><body dir="ltr"><table class="email-wrapper" width="100%" cellpadding="0" cellspacing="0"><tr><td class="content"><table class="email-content" width="100%" cellpadding="0" cellspacing="0"><tr><td class="email-masthead"><a class="email-masthead_name" href="https://example-hermes.com/" target="_blank"><img src="https://uploaddeimagens.com.br/images/001/404/729/original/SIG_1.png?1525586751" class="email-logo" /></a></td></tr><tr><td class="email-body" width="100%"><table class="email-body_inner" align="center" width="570" cellpadding="0" cellspacing="0"><tr><td class="content-cell"><h1>Olá ' +Contato+ ',</h1><p>A <strong>SIG COMBIBLOC </strong>solicitou sua empresa com interesse na realização de serviços. Por favor acesse o link aseguir para concluir esse cadastramento.</p><p>Para o primeiro acesso utilize os dados: <strong></br>login:</strong> '+post1.username+' </br><strong>senha:</strong> 1234qwer</p><table><thead><tr><td><a align="center" href=""><h1>LINK DE ACESSO</h1> </a></td></tr></tbody></table><hr /><p>Em caso de dúvidas entre em contato por: <a href="mailto:mail_HSE@gmail.com">mail_HSE@gmail.com</a> ou pelo telefone: (41)XXXX-XXXX" ou (41)XXXX-XXXX</p><p>Best Regards / Atenciosamente,<br /> Setor HSE-Sig Combibloc</p></td></tr></table></td></tr><tr><td><table class="email-footer" align="center" width="570" cellpadding="0" cellspacing="0"><tr><td class="content-cell"><p class="sub center" style="color:blue"> <strong><h2>SIG Combibloc do Brasil Ltda.</h2></strong><p style="color:blue">Rodovia BR 277 - 120,4 KM</p><p style="color:blue">83605-590 - Campo Largo - Paraná / Brasil</p></p></td></tr></table></td></tr></table></td></tr></table>'
        #msg = EmailMultiAlternatives(subject, text_content, from_email, ['eng_diego@live.com',post1.username])
        #msg.attach_alternative(html_content, "text/html")
        #msg.send()  
        Forr = encoder(str(id))
        print(Forr)
        return redirect('documentosHse', Forr)
    else:
        doc = request.POST.get('nome_documento')
        sel = request.POST.get('sel')
        validade = request.POST.get('Validade')
        if sel == "nada":
            Forr = encoder(str(id))
            return redirect('documentosHse', Forr)
        else:
            obj = documento.objects.get(funcionario=id, nome_documento=doc)
            obj.validade_documento = validade
            obj.hse = sel
            obj.save()
            Forr = encoder(str(id))
        return redirect('documentosHse', Forr)


@permission_required('Hse.add_portaria', login_url="/hse/")
def portaria(request):
    func = funcionario.objects.all()
    emp = empresa_terc.objects.all()
    return render(request, 'portaria.html', {'func':func, 'emp':emp})


def message_fun(request, id):
    if request.method == 'POST':
        form = msgForm(request.POST)
        print (form.errors)
        if form.is_valid():
            post = form.save(commit=False)
            post.data = timezone.now()
            post.ator = request.user.username
            post.save()
            log = logs(num_cham=str(num), ator=request.user.username, acao= request.POST.get("msg"), tipo="msg")
            log.id = None
            log.save()
            Forr = encoder(str(id))
            return redirect('documentosHse', Forr)
    else:        
        form = msgForm()
        For = encoder(str(id))
    return redirect('documentosHse', For)



def doc_integracao(request, id):
    try:
        el = docs_integracao.objects.get(funcionario=id)
    except:
        el = None
    if el:
        el.delete()
    if request.method == 'POST':
        form = doc_Int_Form(request.POST, request.FILES)
        print (form.errors)
        print(request.FILES.get('arquivo'))
        if form.is_valid():
            post = form.save(commit=False)
            post.arquivo = request.FILES.get('arquivo')
            post.funcionario = id
            post.validade_documento = datetime.strptime(request.POST.get('validade_documento'),"%d/%m/%Y").date()
            post.save()
            obj = funcionario.objects.get(id=id)
            print(obj)
            print(obj.data_int)
            obj.data_int = datetime.strptime(request.POST.get('validade_documento'),"%d/%m/%Y").date()
            obj.save()
            print(datetime.strptime(request.POST.get('validade_documento'),"%d/%m/%Y").date())
            For = encoder(str(id))
            return redirect('documentosHse', For)
    else:
        For = encoder(str(id))
        return redirect('documentosHse', For)


def alter(request, num, id):
    el = chamado_hse.objects.get(id=num)
    el.status = "Aguardando HSE" 
    el.resp_terc = request.POST.get('resp')   
    el.save()
    print(el.status)
    aux1 = encoder(str(num))
    aux2 = encoder(str(id))
    return redirect('show_my_cham', aux1,aux2)


def resp(request, idG, numG):
    id = decodif(idG)
    num = decodif(numG)
    respo = cad_resp.objects.get(id=id)
    emp = empresa_terc.objects.all()
    aux = aux_table.objects.filter(id_col=num)
    dist = aux_table.objects.values_list('num_cham', flat=True).distinct()
    obj = chamado_hse.objects.all()
    print(aux)
    return render(request, 'resp.html', {'obj':obj, 'dist':dist, 'respo':respo,'emp':emp, 'aux':aux})

def colaborador(request, id):
  
    data = decodif(id)

    func = funcionario.objects.get(id=data)
    empw = empresa_terc.objects.all()
    return render(request, 'colaborador.html', {'func':func,'empw':empw})       

