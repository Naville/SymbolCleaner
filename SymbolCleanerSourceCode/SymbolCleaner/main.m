//
//  main.m
//  SymbolCleaner
//
//  Created by Zhang Naville on 16/3/15.
//  Copyright © 2016年 NavilleZhang. All rights reserved.
//
#include <stdlib.h>

#import <Foundation/Foundation.h>
#import <mach-o/nlist.h>
char RandomSymbolOffset[4];
static void Usage(){
    NSLog(@"SymbolCleaner PathToFile symoff symnum dysymoff dysymnum OutputPath Arch(32/64)");
    
}
static void randomByte(){
    //int a=arc4random_uniform(900)+100;
   /* while(a <1000){
        a=arc4random_uniform(900)+100;
        
    }*/
    sprintf(RandomSymbolOffset,"%d",0);
}


int main(int argc, const char * argv[]) {
    @autoreleasepool {
        if(argc<4){
            
            Usage();
        }
        else{
            int Arch=atoi(argv[7]);
            NSString* OutPutPath=[NSString stringWithUTF8String:argv[6]];
            NSString* InputPath=[NSString stringWithUTF8String:argv[1]];
            NSLog(@"InputPath:%@",InputPath);
            NSLog(@"Output Path:%@",OutPutPath);
            NSFileHandle* NSFH=[NSFileHandle fileHandleForUpdatingAtPath:InputPath];
            long long  SymOff=atoll(argv[2]);
            long long  SymNumber=atoll(argv[3]);
            int ArchSize=0;
            if (Arch==32){
                ArchSize=sizeof(struct nlist);
            }
            else if (Arch==64){
                ArchSize=sizeof(struct nlist_64);
            }
            else{
                NSLog(@"Wrong Arch");
                exit(255);
            }
            NSMutableData* newSymData=[NSMutableData data];
            for(int index=0;index<SymNumber;index++){
                [NSFH seekToFileOffset:SymOff+index*ArchSize];
                NSMutableData* data=[[NSFH readDataOfLength:ArchSize] mutableCopy];
            
                randomByte();
                [data replaceBytesInRange:NSMakeRange(0,4) withBytes:&RandomSymbolOffset];
                [newSymData appendData:data];
                
            }
            //NSLog(@"%@",newSymData);
            
            NSMutableData* oldData=[NSMutableData dataWithContentsOfFile:InputPath];
            [oldData replaceBytesInRange:NSMakeRange(SymOff, newSymData.length) withBytes:newSymData.bytes];
            [oldData writeToFile:OutPutPath atomically:YES];
            
            
            
            
        }
        
        
    }
    return 0;
}
