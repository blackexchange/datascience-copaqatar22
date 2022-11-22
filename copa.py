import streamlit as st

from htbuilder import HtmlElement, div, ul, li, br, hr, a, p, img, styles, classes, fonts
from htbuilder.units import percent, px
from htbuilder.funcs import rgba, rgb

import pandas as pd
import numpy as np
from scipy.stats import poisson


st.title('🏆 Copa Qatar 2022 🏆')


selecoes = pd.read_excel('dataset/DadosCopaDoMundoQatar2022.xlsx', sheet_name='selecoes', index_col=0)


jogos = pd.read_excel('dataset/DadosCopaDoMundoQatar2022.xlsx', sheet_name='jogos')



### Transformação linear do Ranking

fifa = selecoes['PontosRankingFIFA']

x,b = min(fifa),max(fifa)
fa, fb = 0.15, 1 #Valor estimado para distância
b1 = (fb-fa) /(b-x)
b0= fb - b * b1
forca = b0 + b1 * fifa



def MediasPoisson(selecao1, selecao2):
  forca1 = forca[selecao1]
  forca2 = forca[selecao2]
  mgols = 2.75
  l1 = mgols * forca1/(forca1 + forca2)
  l2 = mgols - l1
  return [l1,l2]

def Resultado(gols1, gols2):
  if (gols1 > gols2):
      Resultado = 'V'
  elif (gols2 > gols1):
    Resultado = 'D'
  else:
    Resultado = 'E'
  return Resultado

Resultado (4,1)

def Pontos(gols1, gols2):
  resultado = Resultado(gols1, gols2)
  if (resultado == 'V'):
    pontos1, pontos2 = 3, 0
  elif (resultado == 'D'):
    pontos1, pontos2 = 0, 3
  else:
    pontos1, pontos2 = 1, 1
  return [pontos1, pontos2, resultado]


def Jogo(selecao1, selecao2):
  l1, l2 = MediasPoisson(selecao1, selecao2)
  gols1 = int(np.random.poisson(lam=l1, size=1) )
  gols2 = int(np.random.poisson(lam=l2, size=1))
  saldo1 = gols1 - gols2 # 5 - 2 = 3
  saldo2 = - saldo1
  pontos1, pontos2, resultado = Pontos(gols1, gols2)
  placar = '{}x{}'.format(gols1, gols2) 
  return  [gols1,gols2,saldo1,saldo2,pontos1,pontos2,resultado, placar]



def Distribuicao(media):
  probs = []
  for i in range(7):
    probs.append(poisson.pmf(i,media))
  probs.append(1 - sum(probs))
  return pd.Series(probs, index = ['0','1','2','3','4','5','6','7+'])



def ProbabilidadesPartida(selecao1, selecao2):
  l1, l2 = MediasPoisson(selecao1, selecao2)
  d1, d2 = Distribuicao(l1), Distribuicao(l2)
  matriz = np.outer(d1,d2)
  vitoria = np.tril(matriz).sum()-np.trace(matriz) #soma infrior
  derrota = np.triu(matriz).sum()-np.trace(matriz) #soma infrior
  empate = 1 - (vitoria + derrota)

  probs = np.around([vitoria, empate, derrota],3)
  probsp = [f'{100*i:.1f}%' for i in probs]

  nomes = ['0','1','2','3','4','5','6','7+']
  matriz = pd.DataFrame (matriz, columns = nomes, index = nomes)
  matriz.index = pd.MultiIndex.from_product([[selecao1], matriz.index])
  matriz.columns = pd.MultiIndex.from_product([[selecao2], matriz.columns])

  output = {'seleção1': selecao1, 'selecao2':selecao2,
            'f1':forca[selecao1], 'f2':forca[selecao2],
            'media1':l1,'media2':l2,
            'probabilidades':probsp, 'matriz':matriz}


  return output

jogos['Vitória'] = None
jogos['Empate'] = None
jogos['Derrota'] = None

for i in range(jogos.shape[0]):
  selecao1 = jogos ['seleção1'][i]
  selecao2 = jogos ['seleção2'][i]
  v, e, d = ProbabilidadesPartida(selecao1, selecao2)['probabilidades']
  jogos.at[i, 'Vitória'] = v
  jogos.at[i, 'Empate'] = e
  jogos.at[i, 'Derrota'] = d


listaSelecoes1 = selecoes.index.tolist()
listaSelecoes1.sort()
listaSelecoes2 = listaSelecoes1.copy()

j1, j2 = st.columns (2)
selecao1 = j1.selectbox('Seleção 1', listaSelecoes1)
listaSelecoes2.remove(selecao1)

selecao2 = j2.selectbox('Seleção 2', listaSelecoes2, index=1)
st.markdown('---')

jogo = ProbabilidadesPartida ( selecao1, selecao2)
prob = jogo['probabilidades']
matriz = jogo['matriz']

col1, col2,col3, col4, col5 = st.columns(5)
col1.image(selecoes.loc[selecao1,'LinkBandeiraGrande'])
col2.metric(selecao1,prob[0])
col3.metric('Empate',prob[1])
col4.metric(selecao2,prob[2])
col5.image(selecoes.loc[selecao2,'LinkBandeiraGrande'])

st.markdown('---')
st.markdown('## 📊 Probabilidades dos Placares')

def fmt(x):
    return f'{str(round(100 * x,1))}%'


st.table(matriz.applymap(fmt))

st.markdown('---')
st.markdown('## ⚽  Probabilidades dos Jogos')

jogoscopa = pd.read_excel('dataset/outputEstimativasJogosCopa.xlsx', index_col=0)

st.table(jogoscopa[['grupo', 'seleção1','seleção2','Vitória', 'Empate', 'Derrota']])


#Footer


def image(src_as_string, **style):
    return img(src=src_as_string, style=styles(**style))


def link(link, text, **style):
  return a(_href=link, _target="_blank", style=styles(**style))(text)


def layout(*args):

    style = """
    <style>
      # MainMenu {visibility: hidden;}
      footer {visibility: hidden;}
     .stApp { bottom: 105px; }
    </style>
    """

    style_div = styles(
        position="fixed",
        left=0,
        bottom=0,
        margin=px(0, 0, 0, 0),
        width=percent(100),
        color="black",
        text_align="center",
        height="auto",
        opacity=1
    )

    style_hr = styles(
        display="block",
        margin=px(8, 8, "auto", "auto"),
        border_style="inset",
        border_width=px(2)
    )

    body = p()
    foot = div(
        style=style_div
    )(
        hr(
            style=style_hr
        ),
        body
    )

    st.markdown(style, unsafe_allow_html=True)

    for arg in args:
        if isinstance(arg, str):
            body(arg)

        elif isinstance(arg, HtmlElement):
            body(arg)

    st.markdown(str(foot), unsafe_allow_html=True)


def footer():
    myargs = ["Criado com ",
              image('https://avatars3.githubusercontent.com/u/45109972?s=400&v=4',
                    width=px(25), height=px(25)), " & ", 
              link("https://www.python.org/", image('https://i.imgur.com/ml09ccU.png',
                width=px(18), height=px(18), margin= "0em")),
              " by ",
              link("https://linkedin.com/in/rodneyneville", "@RodneyNeville"),
              br(),
              link("https://ko-fi.com/D1D6GJN08", image('https://i.imgur.com/thJhzOO.png')),
        
              
    ]
    layout(*myargs)


if __name__ == "__main__":
    footer()