#Introduzir carácteres diferentes. Ex.:ç---------------------------------------------------------------------

#!/usr/bin/env python
#-*- coding:utf-8 -*-

#Declarar biblioteas---------------------------------------------------------------------------------------------------

from StringIO import StringIO
from zipfile import ZipFile
from urllib2 import urlopen
from dateutil.rrule import rrule, DAILY
from PyAstronomy import pyasl
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os.path
import wx
import wx.calendar
import datetime

#Abrir a interface----------------------------------------------------------------------------------------------------------

class Interface(wx.Frame):

    def __init__(self,parent):
        wx.Frame.__init__(self, parent, wx.ID_ANY, "Mare-Graph",size=(800,630))

        #Inserir texto na interface---------------------------------------------------------------------------------------

        wx.StaticText(self, 1, 'START DATE', (160,70))
        wx.StaticText(self, 1, 'STOP DATE', (540,70))

        #Inserir o botão Compute -----------------------------------------------------------------------------------------
        #Interligar com a função OnCompute--------------------------------------------------------------------------------

        compute = wx.Button(self, label="Computer",size=(120,45),pos=(600,530))
        compute.Bind(wx.EVT_BUTTON, self.OnCompute)

        #Criar o botão Close--------------------------------------------------------------------------------------------
        #Interligar com a função Onclose----------------------------------------------------------------------------------
        
        close = wx.Button(self, label="Close",size=(120,45),pos=(450,530))
        close.Bind(wx.EVT_BUTTON, self.OnClose)

        #Criar uma caixa de listagem de seleção múltipla--------------------------------------------------------------------

        sampleList = ['Fortaleza', 'Imbituba', 'Macae', 'Salvador', 'Santana']
        self.ma=wx.ComboBox(self, -1, " Select one Tide Gauges",(70, 400),(200, 30),sampleList, wx.CB_DROPDOWN)

        sampleList = ['Julian Date', 'Calendar Date']
        self.sax=wx.ComboBox(self, -1, "  Select X axis settings", (400, 400),(200, 30),sampleList, wx.CB_DROPDOWN)

        #Criar o botão Select e uma lacauna para inserir a data inicial------------------------------------------------------
        #Interligar com a função show1------------------------------------------------------------------------------------

        self.Selected1 = wx.TextCtrl(self, -1,"Select Start Date",size=(150,25),pos=(160,315))
        self.Button1 = wx.Button(self, label="Select",size=(100,35),pos=(50,310))
        self.Button1.Bind(wx.EVT_BUTTON, self.show1)
        
        #Inserir botão Select e um lacauna para inserir a data final--------------------------------------------------------
        #Interligar com a função show2------------------------------------------------------------------------------------

        self.Selected2 =wx.TextCtrl(self, -1,"Select Stop Date",size=(150,25),pos=(540,315))
        self.Button2 = wx.Button(self, label="Select",size=(100,35),pos=(430,310))
        self.Button2.Bind(wx.EVT_BUTTON, self.show2)

        #Inser os calendários na interface-------------------------------------------------------------------------------
        #Interligar os calendários com a função show1 e show2-------------------------------------------------------------
        
        self.cal1 = wx.calendar.CalendarCtrl(self, 10, wx.DateTime.Now(),size=(300,200),pos=(50,100))
        self.cal1.Bind(wx.calendar.EVT_CALENDAR, self.show1)
        
        self.cal2 = wx.calendar.CalendarCtrl(self, 10, wx.DateTime.Now(),size=(300,200),pos=(430,100))
        self.cal2.Bind(wx.calendar.EVT_CALENDAR, self.show2)
        
    #Definir o formato da data inicial escolhida pelo usuário na interface------------------------------------------------
      
    def show1(self,event):
        c1=self.cal1.GetDate()          
        date1=(c1.Format("%d-%m-%Y"))
        self.Selected1.SetValue(str(date1))
        
    #Definir o formato da data final escolhida pelo usuário na interface--------------------------------------------------

    def show2(self,event):
        c2=self.cal2.GetDate()
        date2=(c2.Format("%d-%m-%Y"))
        self.Selected2.SetValue(str(date2))
        
    #Extrair os dados da internet e realizar a filtragem------------------------------------------------------------------

    def OnCompute(self, event):
        
        #Tornar a variável text global------------------------------------------------------------------------------------
        
        global text
        
        #Chamar as variáveis escolhidas na interface pelo usuário --------------------------------------------------------
        
        mar = self.ma.GetValue()
        sax = self.sax.GetValue()
        di=self.Selected1.GetValue()
        df=self.Selected2.GetValue()
        
        #Informar ao usuário com uma mensagem de erro caso as datas não forem preenchidas----------------------------------
        
        if df=='Select Stop Date':
            wx.StaticText(self, 1, 'Error Stop Date', (200,530))
            return(self)
        
        elif di=='Select Start Date':
            wx.StaticText(self, 1, 'Error Start Date', (200,530))
            return(self)
        
        elif df=='Select Stop Date' and di=='Select Start Date':
            wx.StaticText(self, 1, 'Error Start and Stop Date ', (200,530))
            return(self)
        
        #Transformar o formato de data escolhido na interface para dia-mês-ano--------------------------------------------
        
        a=datetime.datetime.strptime(di, "%d-%m-%Y").date()
        b=datetime.datetime.strptime(df, "%d-%m-%Y").date()
        
        #Informar o usuário com uma mensagem de erro caso a data inicial for maior que a final-----------------------------
       
        if (b>a)==True:
            a=a
            b=b
        
        else:
            wx.StaticText(self, 1, 'Error: Stop Date < Star Date', (200,530))
            return(self)
        
        #Definir latitude e longitude aos marégrafos----------------------------------------------------------------------
        #Selecionar as três primeiras letras do nome dos marégrafos para associar ao link---------------------------------

        if mar=="Fortaleza":            
            lat="03°42’52.55”S"
            lon="38°28’36.54”O"
            lk="FOR"
        elif mar=="Imbituba":
            lat= "28°13’52.30”S"
            lon="48°39’2.06”O"
            lk="IMB"
        elif mar=="Macae":
            lat="22°23’08” S"
            lon= "41°46’10” O"
            lk="MAC"
        elif mar=="Salvador":
            lat="12°58’26.29”S"
            lon="38°31’1.95” O"
            lk="SAL"
        elif mar=="Santana":
            lat="00°03’41” S"
            lon="51°10’04” O"
            lk="SAN"
        
        #Informar uma mensagem de erro caso o usuario nao informar um marégrafo-------------------------------------------
        
        else:
            wx.StaticText(self, 1, 'Select one Tide Gauge', (200,530))
            return(self)
           
        #Extrair e deszipar os dados maregraficos do site do IBGE---------------------------------------------------------
        
        mar=str(mar)  
        dia=hora=valor=[]
        for dt in rrule(DAILY, dtstart=a, until=b):
            ymd=dt.strftime("%y%m%d") 
            md=dt.strftime("%d%m")
            link=('https://geoftp.ibge.gov.br/informacoes_sobre_posicionamento_geodesico/rmpg/dados/%s/%s%s.zip' %(md,lk,ymd))
            url =urlopen(link)
            zf = ZipFile(StringIO(url.read()))
            
            #Ler e unir os dados de diferetes arquivos--------------------------------------------------------------------
            
            for item in zf.namelist():
                dads=StringIO(zf.read(item))
                dads = np.genfromtxt(dads, dtype=None)
                dads = np.char.replace(dads, ',', '.') 
                dia=np.append(dia,[dads[:,0]])
                hora=np.append(hora,[dads[:,1]])
                valor=np.append(valor,[dads[:,2]]) 
        dads=np.concatenate([[dia],[hora],[valor]])
        dads=np.transpose(dads)

        #Filtrar os dados disponíveis num intervalo de 5 minutos----------------------------------------------------------
        
        dia2=hora2=valor2=[]
        for hor in range(0,24,1):    
            for minu in range(0,56,5):
                d=np.delete(dads, np.where((dads[:,1])!=('%.2d:%.2d:00' %(hor,minu)) )[0], 0)
                dia2=np.append(dia2,[d[:,0]])
                hora2=np.append(hora2,[d[:,1]])
                valor2=np.append(valor2,[d[:,2]]) 
        d=np.concatenate([[dia2],[hora2],[valor2]])
        d1=np.transpose(d)

        dia3=hora3=valor3=[]
        for dtt in rrule(DAILY, dtstart=a, until=b):
            dtt=dtt.strftime("%d/%m/%Y")
            d=np.delete(d1, np.where((d1[:,0])<>('%s' %(dtt)) )[0], 0)
            dia3=np.append(dia3,[d[:,0]])
            hora3=np.append(hora3,[d[:,1]])
            valor3=np.append(valor3,[d[:,2]]) 
        d=np.concatenate([[dia3],[hora3],[valor3]])
        d=np.transpose(d)

        #Coeficientes Fm do filtro descrita em PUGH (1987,p.416)-----------------------------------------------------------

        coef=np.matrix([[0.0648148,0.0643225,0.0628604,0.0604728,0.0572315,0.0532331,0.0485954,0.0434525,0.0379505,0.0322412,
        0.0264773,0.0208063,0.0153661,0.0102800,0.0056529,0.0015685,-0.0019127,-0.0047544,-0.0069445,-0.0084938,
        -0.0094346,-0.0098173,-0.0097074,-0.0091818,-0.0083247,-0.0072233,-0.0059642,-0.0046296,-0.0032942,-0.0020225,
        -0.0008672,0.0001321,0.0009493,0.0015716,0.0019984,0.0022398,0.0023148,0.0022492,0.0020729,0.0018178,
        0.0015155,0.0011954,0.0008830,0.0005986,0.0003568,0.0001662,0.0000294,-0.0000560,-0.0000970,-0.0001032,
        -0.0000862,-0.0000578,-0.0000288,-0.0000077,0.0000000]])
        coef=np.transpose(coef)
        l=len(d)-288
        v1=v2=dat=tim=jul=julday=datenum=datatemp=[]
        
        # Primeira parte da equação (x1) de filtragem descrita em PUGH (1987,p.416)------------------------------------------------
        
        for j in range(288,l,12):
            data=str(d[j,0])
            time=str(d[j,1])    
            x1=np.multiply(float(coef[0,0]),float(d[j,2]))
            dat=np.append(dat,data)
            tim=np.append(tim,time)
            v1=np.append(v1,x1)

             # Segunda parte da equação (x2) de filtragem descrita em PUGH (1987,p.416)------------------------------------

            for i in range(1,55,1):
                x2=np.multiply(float(coef[i,0]),(float(d[(j+i),2])+float(d[(j-i),2])))
                v2=np.append(v2,x2)
        v1=np.transpose(np.array(v1))
        v2=np.transpose(np.array([v2]))
        vv2=[]
        for n in range(0,len(v2),54):
            m=n+53
            vv2=np.append(vv2,np.sum(v2[n:m,:1]))
        vv2=np.transpose(np.array(vv2))
        val=v1+vv2
              
        for y in range(0,(len(tim)),1):
            datt=np.matrix(dat)
            timm=np.matrix(tim)
            day, month, year = (int(x) for x in (datt[0,y]).split('/'))
            hour, minute, secund = (int(x) for x in (timm[0,y]).split(':'))
            dt = datetime.datetime(year, month, day, hour,minute,secund)
            datenum=np.append(datenum,mdates.date2num(dt))
            julday=np.append(julday,[pyasl.jdcnv(dt)])
        julday=np.transpose(np.array([julday]))
        datenum=np.transpose(np.array(datenum))
     
        #Formatar o arquivo txt-------------------------------------------------------------------------------------------
        
        col_data={'Date':dat,'Time':tim,'SeeLevel':val}
        text= pd.DataFrame(data=col_data)
        pd.set_option('max_rows', len(text))
        text = text[['Date', 'Time','SeeLevel']]
        text=text.to_string(index=False)
     
        #%matplotlib notebook
        f, axs = plt.subplots(1,1,figsize=(15,5))
        plt.xticks(rotation=85)
        ax=plt.gca()
        ttil= ('\n Sea Level obtained from %s Tide Gauge\n Lat: %s | Long: %s (SIRGAS 2000)\n'%(mar,lat,lon))
        
        #Definir o eixo X em Dia Juliano ou em Data do calendário e plotar o gráfico--------------------------------------
    
        if sax=='Calendar Date':
            ax.xaxis_date()
            xfmt = mdates.DateFormatter('%d-%m-%y  %H:%M:%S')
            ax.xaxis.set_major_formatter(xfmt)
            ax.plot(datenum,val,color='r',linestyle='-', linewidth=1)
            ax.set(xlabel='Time', ylabel='Sea Level (m)',
                title=(ttil.decode('utf-8')))
            plt.gcf().autofmt_xdate()
            plt.grid()
            plt.show()
        elif sax=='Julian Date':
            ax.plot(julday,val,color='r',linestyle='-', linewidth=1)
            ax.set(xlabel='Julian Date', ylabel='Sea Level (m)',
                   title=(ttil.decode('utf-8')))
            plt.gcf().autofmt_xdate()
            plt.grid()
            plt.show()
            
        #Informar o usuário com uma mensagem de erro caso o usuario nao escolher uma configuração de data para o eixo X----
        
        else:
            wx.StaticText(self, 1, 'Select one X axis', (200,530))
            return(self)
            
        self.Destroy()
        self.Salve = MainWindow(wx.Frame)
        self.Salve.Show()
    #Encerrar o programa caso o usuário apertar em Close na interface------------------------------------------------------    
    def OnClose(self, event):
        self.Destroy()
        
#Salvar o arquivo em txt---------------------------------------------------------------------------------------------------

class MainWindow(wx.Frame):
    def __init__(self,parent):
        super(MainWindow, self).__init__(None, size=(400,200))
        self.SetTitle('Process Completed Successfully')
        compute = wx.Button(self, label="Salve as",size=(80,25),pos=(150,150))
        compute.Bind(wx.EVT_BUTTON, self.OnSaveAs)

    def OnSaveAs(self,Interface):
        dialog = wx.FileDialog(self, "Save to file:", ".", "", "Text (*.txt)|*.txt", wx.SAVE|wx.OVERWRITE_PROMPT)
        if dialog.ShowModal() == wx.ID_OK:
            self.filename = dialog.GetFilename()
            self.dirname = dialog.GetDirectory()
            textfile = open(os.path.join(self.dirname, self.filename), 'w')
            np.savetxt(textfile, np.column_stack(text),delimiter=' ', fmt='%.4s')
        
        #Fechar o programa------------------------------------------------------------------------------------------------
        
        dialog.Destroy()
        self.Destroy()

#Mostrar a interface inicial----------------------------------------------------------------------------------------------

def main():
    app = wx.App()
    Interface(None).Show()
    app.MainLoop()
if __name__ == '__main__':
    main()