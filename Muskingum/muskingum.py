def muskingum(k,x,t,I):
    c0=round((0.5*t-k*x)/(0.5*t+k-k*x),3)
    c1=round((0.5*t+k*x)/(0.5*t+k-k*x),3)
    c2=round((-0.5*t+k-k*x)/(0.5*t+k-k*x),3)
    c0i2_1=[0.0];    c1i1_1=[0.0];    c2o1_1=[0.0];    o2_1=[0.0]
    c0i2_2=[0.0];    c1i1_2=[0.0];    c2o1_2=[0.0];    o2_2=[0.0]
    c0i2_3=[0.0];    c1i1_3=[0.0];    c2o1_3=[0.0];    o2_3=[0.0]

    "river 1"
    i_before=2240;
    o_before=2280;
    I1=I
    i=0
    o2_1[i]=o_before
    while(o2_1[i]>=100):
        i=i+1
        if i>=len(I):
            I1.append(0)
        c0i2_1.append(round(c0*I1[i],3))
        c1i1_1.append(round(c1*I1[i-1],3))
        c2o1_1.append(round(c2*o2_1[i-1],3))
        o2_1.append(round(c0i2_1[i]+c1i1_1[i]+c2o1_1[i],3))
        if o2_1[i]<0.0001:
            break
    '''
    print("c0i2_1:")
    print(c0i2_1)
    print("c1i1_1:")
    print(c1i1_1)
    print("c2o1_1:")
    print(c2o1_1) 
    print("o2_1:")
    print(o2_1)
    '''

    "river 2"
    i_before=2280;
    o_before=2320;
    I2=o2_1
    i=0
    o2_2[i]=o_before;
    while(o2_2[i]>=100):
        i=i+1
        if i>=len(I2):
            I2.append(0)
        c0i2_2.append(round(c0*I2[i],3))
        c1i1_2.append(round(c1*I2[i-1],3))
        c2o1_2.append(round(c2*o2_2[i-1],3))
        o2_2.append(round(c0i2_2[i]+c1i1_2[i]+c2o1_2[i],3))
        if o2_2[i]<0.0001:
            break
    '''
    print("c0i2_2:")
    print(c0i2_2)
    print("c1i1_2:")
    print(c1i1_2)
    print("c2o1_2:")
    print(c2o1_2) 
    print("o2_2:")
    print(o2_2)
    '''

    "river 3"
    i_before=2320;
    o_before=2370;
    I3=o2_2
    i=0
    o2_3[i]=o_before;
    while(o2_3[i]>=100):
        i=i+1
        if i>=len(I3):
            I3.append(0)
        c0i2_3.append(round(c0*I3[i],3))
        c1i1_3.append(round(c1*I3[i-1],3))
        c2o1_3.append(round(c2*o2_3[i-1],3))
        o2_3.append(round(c0i2_3[i]+c1i1_3[i]+c2o1_3[i],3))
        if o2_3[i]<0.0001:
            break
    '''
    print("c0i2_3:")
    print(c0i2_3)
    print("c1i1_3:")
    print(c1i1_3)
    print("c2o1_3:")
    print(c2o1_3) 
    print("o2_3:")
    print(o2_3)
    '''
#    print("k="+str(k))
#    print("x="+str(x))
    
    return o2_3
