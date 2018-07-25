from django.db import models
from django.conf import settings
from datetime import datetime
from django.contrib.auth.models import User
from cadastro.models import empresa_terc, cad_resp

default = 'default.png'

class chamado_hse(models.Model):
	solicitante = models.CharField(max_length=100)
	data_abertura = models.DateTimeField(auto_now_add=True)
	empresa = models.ForeignKey(empresa_terc, on_delete=models.CASCADE)
	tempo_estimado = models.CharField(max_length=100)
	nome_proj = models.CharField(max_length=100)
	setor_solicitante = models.CharField(max_length=100)
	gestor_solicitante = models.CharField(max_length=100)
	tipo_servico = models.CharField(max_length=50, blank=True)
	descricao = models.CharField(max_length=1000, blank=True)
	email_terc = models.CharField(max_length=500)
	email_solicitante = models.CharField(max_length=100)
	fone_solicitante = models.CharField(max_length=100)
	status = models.CharField(max_length=100)
	data = models.DateField(auto_now=True)
	resp_terc = models.CharField(max_length=100)

	def __str__(self):
		return '{}'.format(self.id)

class aux_table(models.Model):
	num_cham = models.IntegerField()
	tps = models.CharField(max_length=100)
	colab = models.CharField(max_length=100)
	id_col = models.CharField(max_length=55)
	status = models.CharField(max_length=10, default="AG")

	def __str__(self):
		return '{}'.format(self.id)

"""
class Solic_cad(models.Model):
	solicitante = models.CharField(max_length=100)
	nome_empresa = models.CharField(max_length=100)
	obs = models.CharField(max_length=500)
	first_access = models.IntegerField()

	def __str__(self):
		return '- {}'.format(self.Empresa)"""


class logs(models.Model):
	num_cham = models.CharField(max_length=100)
	ator = models.CharField(max_length=100)
	acao = models.CharField(max_length=10000)
	data = models.DateTimeField(default=datetime.now)
	tipo = models.CharField(max_length=100, default=None)

	def __str__(self):
		return '{}'.format(self.id)

class msg(models.Model):
	num_cham = models.CharField(max_length=100)
	ator = models.CharField(max_length=100)
	msg = models.CharField(max_length=10000)
	data = models.DateTimeField(default=datetime.now)
	tipo = models.CharField(max_length=10, default=None)
	id_col = models.CharField(max_length=10, default=None)

	def __str__(self):
		return '{}'.format(self.id)


class Hse(models.Model):
	Nome = models.CharField(max_length=10, default=None)

	def __str__(self):
		return '{}'.format(self.Nome)


class portaria(models.Model):
	Nome = models.CharField(max_length=10, default=None)

	def __str__(self):
		return '{}'.format(self.Nome)

