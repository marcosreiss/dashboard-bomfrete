import psycopg2 as psy
import pandas as pd

def load_ordemcar_from_sql():

    query = "SELECT * FROM ordemcar"
   
    with psy.connect(
            host='satbomfrete.ddns.net',
            port='5409',
            user='eurico',
            password='SAT1234',
            database='bomfrete'
        ) as connection:
            df_logistica = pd.read_sql_query(query, connection)

    df_logistica.dropna(how='all', axis=1, inplace=True)
    
    columns=[
    'codordemcar', 'numero', 'codfilial', 'codcliente', 'codremetente', 'coddestinatario', 'numeropedido',
    'data', 'dataatual', 'datadigitacao', 'codcidadeorigem', 'codcidadedestino', 'codcoleta', 'codentrega',
    'codveiculo', 'codmotorista', 'codmercadoria', 'usuarioins', 'usuarioalt', 'pesosaida', 'codunidadeembarque',
    'precotonmotorista', 'obs', 'obs1', 'obs2', 'obs3', 'obs4', 'quantmercadoria', 'especiemercadoria', 'tipo',
    'numeroviagem', 'codgerrisco', 'codconsignatario', 'cancelado', 'datacanc', 'usuariocanc', 'codrota',
    'listacoddestinatario', 'pedidofrete', 'pedidotransf', 'pedidocliente2', 'codespeciemerc', 'kmini', 'emitida',
    'codembarcador', 'impresso', 'motivocancelado', 'libgerriscoprop', 'tnfrete', 'contratopedido', 'ordemvenda',
    'protocolo', 'parceiro', 'pesocubado', 'status', 'datavalidade', 'previsaochegada', 'numautgerrisco',
    'dataenvgerrisco', 'codmotivocanc', 'codcontrato', 'codcoletasetor', 'codentregasetor', 'codordemcarant',
    'numeroseguro', 'expseguro', 'codgerriscoseg', 'arqxml', 'percadiantmotorista', 'precotonadtomot',
    'codfornecedoradiant', 'horainicarreg', 'horafimcarreg', 'statuslog', 'ordemcli', 'codcidadeorigem2',
    'codcidadedestino2', 'codcidadetrocanota', 'codcoleta2', 'codentrega2', 'precotonempresa', 'freteempresa',
    'fretemotorista', 'porccomissaoemb', 'vlcomissaoemb', 'codgerriscoped', 'codgerriscop', 'outrosdescontosmot2',
    'codfrete', 'checklistpagto', 'valorapolice', 'adtointegracao', 'percadtointegracao', 'lavagem', 'abastecimentointerno',
    'checklistrobosat'
    ]

    df_logistica = df_logistica.drop(columns=columns, errors='ignore')

    return df_logistica
