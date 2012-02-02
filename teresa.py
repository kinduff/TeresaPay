#!/usr/bin/python
# -*- coding: utf-8 -*-
import pygame
import Image
from pygame.locals import *
import sys
import random
import os
import tweepy
import datetime
import opencv
from opencv import highgui
import pycurl
import cStringIO
import urllib, urllib2, base64, re
import untangle
import optparse
from Tkinter import *
import time

#Variables
filename = "pic.jpg" #Esto lo uso despues para enviar imagen a Imgur o enviar link a twitter

#Twitter config
#En esta parte van tus keys, las sacas haciendo una app en api.twitter.com y activando el read&write
CONSUMER_KEY = ''
CONSUMER_SECRET = ''
ACCESS_KEY = ''
ACCESS_SECRET = ''
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET) #Tweepy
auth.set_access_token(ACCESS_KEY, ACCESS_SECRET) #Necesita
api = tweepy.API(auth) #Esto para funcionar

#Imgur upload
def upload_from_computer(image): #Funcion para subir imagen con variable para que sea facil de llamar
    response = cStringIO.StringIO() #Variable para recibir respuesta de la API
    c = pycurl.Curl() #Abreviamos para no poner siempre todo el rollo, aqui utilizamos pycurl
    
    values = [
              ("key", "73753e92b5c8bbd2105cb65f456f10ed"), #Esta key no la oculto porque es anonima, puedes sacar la tuya o utilizar esta
              ("image", (c.FORM_FILE, filename))] #Valor a enviar, llamamos al filename que puse arriba
    
    c.setopt(c.URL, "http://api.imgur.com/2/upload.xml") #¿Eres tu señor XML? Si joven, ¿Que se le ofrece?
    c.setopt(c.HTTPPOST, values) #¿Te puedo leer?
    c.setopt(c.WRITEFUNCTION, response.write) #Claro que si, aqui tienes
    c.perform() #Interesante
    c.close() #Kthxbye
    
    return response.getvalue() #Y tenemos los valores del XML

#Imgur xml response process
def process(xml): #Procesamos al señor XML
    o = untangle.parse(xml) #Nos facilitamos la vida y parseamos el XML
    url = o.upload.links.original.cdata #Extraemos el link de la imagen subida
    #delete_page = o.upload.links.delete_page.cdata #Esto es para obtener el link para eliminar la imagen subida
    tw2 = textweet.get() #Obtenemos valor del campo de texto, osea el tweet a enviar
    api.update_status(''+ tw2 + ' ' + url + '') #Tweet + Imagen subida
    print ('\n------------------\n=== Tweet enviado ===\n'+ tw2 +'\n\n=== Foto subida ===\n'+ url +'\n\n=== Enviado con exito ===\nSi\n------------------\n') #Log en terminal
    texttw.delete(0, END) #Borramos campo de texto
    lasttweet() #Obtenemos ultimo tweet

#Time
now = datetime.datetime.now() #Funcion para obtener la hora
wakeup = now.strftime("#KinduffEstaOnline entro a las %H:%M del %d-%m-%Y") #Parseamos la hora y agregamos un tweet [ver holahola()]

#Uptime
def uptime(): #Envia tweet mostrando cuanto tiempo lleva la pc prendida
     try:
         f = open( "/proc/uptime" ) #Vital para obtener el valor
         contents = f.read().split()
         f.close()
     except:
        return "Cannot open uptime file: /proc/uptime" #No usas linux, sorry
#Aqui se parsea y se sintetiza, muy personalizable
     total_seconds = float(contents[0])
     MINUTE  = 60
     HOUR    = MINUTE * 60
     DAY     = HOUR * 24
     days    = int( total_seconds / DAY )
     hours   = int( ( total_seconds % DAY ) / HOUR )
     minutes = int( ( total_seconds % HOUR ) / MINUTE )
     seconds = int( total_seconds % MINUTE )
     string = ""
     if days > 0:
         string += str(days) + " " + (days == 1 and "dia" or "dias" ) + ", "
     if len(string) > 0 or hours > 0:
         string += str(hours) + " " + (hours == 1 and "hora" or "horas" ) + ", "
     if len(string) > 0 or minutes > 0:
         string += str(minutes) + " " + (minutes == 1 and "minuto" or "minutos" ) + ", "
     string += str(seconds) + " " + (seconds == 1 and "segundo" or "segundos" )
     return string;
times = uptime() #Entregamos valor

#Imprimir home timeline
def timeline():
	taimlain = api.user_timeline(count="1") #No es un typo, es falta de imaginación para nombrar variables
	for tweet in taimlain: 
            #str1 = tweet.text
            #textarea.insert(0.0, str1) #Aqui se imprime en un textarea en Tkinter pero obviamente lo imprimer alrevez
	    print tweet.text+"\n" #Se imprime timeline en terminal

#Ultimo status o tweet del usuario
#Se imprime en el grid que hice (ver ultimas lineas), igual se puede imprimir en terminal
def lasttweet():
    lasttw = Label(root, text="                                             ")
    lasttw.grid(row=4, column=1)
    superlast = api.user_timeline(count="1")
    for tweet in superlast:
        lasttw = Label(root, text=tweet.text)
        lasttw.grid(row=4, column=1)

#Apagando la pc
def byebye(): #Mandamos uptime()
    api.update_status('#KinduffSeVa estuvo: %s online.' % (times))
    lasttweet()

#Prendiendo la pc
def holahola(): #Saludamos
    api.update_status((wakeup))
    lasttweet()

#Tomamos imagen con camara y enviamos a imgur [ver upload_from_computer(img)]
def picture():
	sock = cStringIO.StringIO()
	camera = highgui.cvCreateCameraCapture(0)
	def get_image(): #Creamos camara
	    im = highgui.cvQueryFrame(camera)
	    im = opencv.cvGetMat(im)
	    return opencv.adaptors.Ipl2PIL(im) 

	fps = 30.0 #Frames per second
	pygame.init()
	window = pygame.display.set_mode((640,480)) #Tamaño
	pygame.display.set_caption("Twitter") #Titulo
	screen = pygame.display.get_surface() #Mostramos camara

	while True:
	    events = pygame.event.get()
	    im = get_image()
	    pg_img = pygame.image.frombuffer(im.tostring(), im.size, im.mode)
	    screen.blit(pg_img, (0,0))
	    pygame.display.flip() #Flipeamos la imagen
	    pygame.time.delay(int(1000 * 1.0/fps)) #Actualizamos frames
	    for event in events:
		if event.type == KEYDOWN:
		    if event.key == K_SPACE: #Tomamos foto con barra espaciadora
		        pygame.image.save(pg_img, filename)
		        img = filename
		        xml = upload_from_computer(img)
		        process(xml) #Enviamos a imgur
		        sys.exit(0) #No encontre la forma de cerrar la ventana de la camara, con esto se cierra todo el programa
		    if event.key == K_ESCAPE: #Cerramos la camara al presionar ESC
		        sys.exit(0) 

#Enviar un tweet personalizado
def tweet():
  api.update_status('%s' % textweet.get()) #Tomamos valor de campo de texto y enviamos
  print ('Tweet enviado: %s' % textweet.get()) #Se imprime tweet en terminal
  texttw.delete(0, END) #Borramos el campo de texto
  lasttweet() #Mostramos ultimo tweet

#Para utilizarse bajo la terminal, habra que modificar todo el script para que vuelva a funcionar
#ya que para que se lograra integrar con Tkinter modifique varias funciones
def main():
  t = optparse.OptionParser(description='Diferentes utilidades para twitter.',
                                   prog='teresa.py',
                                   version='teresa v0.1',
                                   usage='%prog --opcion "variable"')
  t.add_option('-n', '--hola', help='Hola twitter.')
  t.add_option('-b', '--bye', help='Adios twitter.')
  t.add_option('-t', '--tw', help='Envia un tweet basico.')
  t.add_option('-p', '--picture', help='Toma una foto y la sube a twitter.')
  t.add_option('-m', '--timeline', help='Devuelve timeline.')
  options, arguments = t.parse_args()
  if options.tw:
    tweet(options.tw)
  elif options.picture:
    picture(options.picture)
  elif options.timeline:
    timeline()
  elif options.bye:
    byebye()
  elif options.hola:
    holahola()
  #else:
    #t.print_help()

#Interfaz grafica con Tkinter
root = Tk()
lasttweet() #Obtenemos ultimo tweet de una vez

#El famoso textarea con scroll
#boot = Toplevel()
#fr = Frame(boot)
#boot.title('Teresa.pay 2')
#fr.pack()
#textarea = Text(fr, height=20, width=40)
#scroll = Scrollbar(fr, command=textarea.yview)
#textarea.configure(yscrollcommand=scroll.set)
#textarea.pack(side=LEFT)
#scroll.pack(side=RIGHT, fill=Y)

root.title('Teresa.pay') #Titulo

#Botones que llevana funciones y con grid() se posicionan
textweet = StringVar()
texttw = Entry(root, textvariable=textweet, width=30)
texttw.grid(row=1, column=1)
lanzar = Button(root, text="Enviar tweet",command=tweet, width=20)
lanzar.grid(row=2, column=1)
lanzar = Button(root, text="Tweet + Foto",command=picture, width=20)
lanzar.grid(row=1, column=2)
lanzar = Button(root, text="Mostrar timeline",command=timeline, width=20)
lanzar.grid(row=2, column=2)
lanzar = Button(root, text="Online",command=holahola, width=20)
lanzar.grid(row=3, column=2)
lanzar = Button(root, text="Offline",command=byebye, width=20)
lanzar.grid(row=4, column=2)
lanzar = Button(root, text="Ultimo Tweet",command=lasttweet, width=20)
lanzar.grid(row=3, column=1)

root.mainloop()

if __name__ == '__main__':
  main()
