


#include "sapucx.h"
#include "sapuc.h"
#include "sapnwrfc.h"

int mainU(int argc, SAP_UC** argv) {
       SAP_UC* big = new SAP_UC[214958081];
       for (int i = 0; i < 214958080; ++i)
             big[i] = cU('a');
       big[214958080] = 0;
 
       size_t length = strlenU(big);
       printfU(cU("Length: %u\n"), (unsigned long)length);
 
       delete[] big;
       return 0;
}