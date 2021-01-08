# Covid19MalletCrawler

This script downloads images from the city hall website and uses OCR Tesseract to extract the text with Covid19 data and organizing in  dataframes, cleaning and then exporting to a csv table.

Este script faz o download de imagens no site da prefeitura e usa OCR Tesseract para extrair o texto com os dados do Covid19 organizando em um dataframe, limpando e em seguida exporta para uma  tabela csv.


* Covid19_mallet_automate.ipynb:
Contém o jupyter Notebook para desenvolvimento do código
* CovidCrawlerScript.py:
Script que executa um webcrap baixando todas as imagens do site e em seguida extrai o texto das imagens através do OCR, separando os dados em chaves/valores em loop e  adiconando tudo em uma planilha CSV para processamento posterior.

* CovidGraphs.ipynb:
Processa o dataframe ordenando por data e removendo caractesres indesejados

TODO: Aplicativo para celular com os dados atualizados e gráficos estátisticos.
(Como o site parou de atualizar os dados em dezembro, meu  projeto parou)

URL da prefeitura com as images: http://mallet.pr.gov.br/Site_mallet/materias/2020/03_marco/18_covid_oficio/18_covid_oficio.asp

mais em:
https://www.kaggle.com/evertonkozloski/kernel5747cb5483
