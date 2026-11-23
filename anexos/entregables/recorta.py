from PIL import Image, ImageDraw
import glob
for f in glob.glob('cap/*.png'):
    if f.endswith('_fig.png'): continue
    im=Image.open(f).convert('RGB'); W,H=im.size
    xs=[int(W*k) for k in (0.1,0.3,0.5,0.7,0.9)]
    gris=lambda y: all(240>im.getpixel((x,y))[0]>215 for x in xs)
    blanca=lambda y: all(im.getpixel((x,y))[0]>=250 for x in xs)
    y0=next(y for y in range(int(H*0.05),H) if blanca(y))
    y1=next((y for y in range(y0+200,H-3) if gris(y) and gris(y+2)),H)
    c=im.crop((int(W*0.025),y0,int(W*0.975),y1-2)); w,h=c.size
    ImageDraw.Draw(c).rectangle((int(w*0.72),h-int(115*W/2160),w-1,h-1),fill=(255,255,255))
    c.save(f.replace('.png','_fig.png')); print(f,c.size)
