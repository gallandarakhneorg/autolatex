size(6cm,0);
import math;

// Placement de 4 points
pair A=(0,0),B=(2,2),C=(0,5),D=(5,1);
dot("$A$",A,SE);
dot("$B$",B,SE);
dot("$C$",C,N);
dot("$D$",D,N);

// Tracé de [AB] et [CD]
draw(A--B,blue);
draw(C--D,red);

// Construction du point
// d'intersection de (AB) et (CD)
pair pI=extension(A,B,C,D);
dot("$I$",pI,N,red);
draw(B--pI,1pt+dotted);

