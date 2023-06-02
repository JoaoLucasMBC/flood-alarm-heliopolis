from flask_restful import Resource
from flask import request
from model.models import UsuarioModel

import os


class ListUsuario(Resource):
    '''
    Rotas para listar e criar usuários
    '''

    def get(self):
        '''
        Rota GET para listar todos os usuários

        Return:
            json: lista de usuários
        '''

        usuarios = UsuarioModel.list_all()

        return {'usuarios': [usuario.to_dict() for usuario in usuarios]}, 200


    def post(self):
        '''
        Rota POST para criar um novo usuário

        Parâmetros:
            nome: nome do usuário
            regiao: região do usuário
            numero: número do usuário
        
        Header:
            Secret: chave de autenticação do formulário

        Return:
            json: usuário criado
        '''

        # verifica se o header Secret foi passado
        receivedSignature = request.headers.get("Secret")

        # sem chave secreta, não há permissão
        if receivedSignature is None:
            return {'error': 'Permission denied.'}, 403
        
        # verifica se a chave secreta é válida
        if(receivedSignature != os.environ.get('TYPEFORM_SECRET_KEY')):
            return {'error': 'Invalid signature. Permission Denied.'}, 403
        
        # separa as perguntas e respostas do formulário
        questions = request.json['form']['questions']
        answers = request.json['answer']['answers']

        # para cada resposta, identifica a pergunta e salva o valor
        for ans in answers:
            ans_id = ans['q']

            for ques in questions:
                if ques['_id'] == ans_id:
                    if 'nome' in ques['question']:
                        nome  = ans['t']
                    if 'celular' in ques['question']:
                        numero = ans['t']
                    if 'Em qual' in ques['question']:
                        regiao = ans['c'][0]['t']


        # cria o usuário
        usuario = UsuarioModel(nome=nome, regiao=regiao, numero=numero)
        usuario.save()

        return usuario.to_dict(), 201


class Usuario(Resource):
    '''
    Rotas para buscar e deletar um usuário
    '''

    def get(self, usuario_id):
        '''
        Rota GET para buscar um usuário pelo id

        Parâmetros:
            usuario_id: id do usuário
        
        Return:
            json: usuário encontrado
        '''

        usuario = UsuarioModel.find_by_id(id=usuario_id).first()

        if usuario:
            return usuario.to_dict(), 200
        
        return {'message': 'Usuario not found.'}, 404


    def delete(self, usuario_id):
        '''
        Rota DELETE para deletar um usuário pelo id

        Parâmetros:
            usuario_id: id do usuário
        
        Return:
            json: mensagem de sucesso ou erro
        '''

        usuario = UsuarioModel.query.filter_by(id=usuario_id).first()

        if usuario:
            usuario.delete()
            return {'message': 'Usuario deleted.'}, 200
        
        return {'message': 'Usuario not found.'}, 404