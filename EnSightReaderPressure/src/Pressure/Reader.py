'''
Created on 2013/10/22

@author: tshimizu
'''
import struct
import os

class Pressure:
    def __init__(self, geoName, pName, rho):
        self.geoName = geoName
        self.pName = pName
        self.rho = rho
        self.tria_p = []
        self.quad_p = []
        self.nsided_p = []
        self.Max = rho * 27.78 * 27.78 * 0.5 * 2.0
        self.Min = -1.0 * rho * 27.78 * 27.78 * 0.5 * 4.0
        
    def readGeo(self):
        self.tria3 = 0
        self.quad4 = 0
        self.nsided = 0
        #--- read file for .geo
        inGeoFile = open(self.geoName,'r')
        for line in inGeoFile:
            if line.strip() == 'tria3':
                self.tria3 = inGeoFile.next().strip()
            if line.strip() == 'quad4':
                self.quad4 = inGeoFile.next().strip()
            if line.strip() == 'nsided':
                self.nsided = inGeoFile.next().strip()
        inGeoFile.close() 
        
    def getTria3(self):
        return self.tria3
    
    def getQuad4(self):
        return self.quad4
    
    def getNsided(self):
        return self.nsided
    
    def getTriaP(self):
        return self.tria_p
    
    def getQuadP(self):
        return self.quad_p
    
    def getNsidedP(self):
        return self.nsided_p
    
    def readP(self):
        infile = open(self.pName, 'rb')
        print '1. signed char (80): %s' % struct.unpack('80s', infile.read(80))
        print '2. signed char (80): %s' % struct.unpack('80s', infile.read(80))
        print '3. int: %i' % struct.unpack('i', infile.read(4))
        if int(self.tria3) > 0:
            print '4. signed char (80): %s' % struct.unpack('80s', infile.read(80))
            for i in range(0, int(self.tria3)):
                b = struct.unpack('f', infile.read(4))
                for bb in b:
                    p = bb * self.rho
                    self.tria_p.append(max(self.Min, min(self.Max, p)))
        if int(self.quad4) > 0:
            print '6. signed char (80): %s' % struct.unpack('80s', infile.read(80))
            for i in range(0, int(self.quad4)):
                b = struct.unpack('f', infile.read(4))
                for bb in b:
                    p = bb * self.rho
                    self.quad_p.append(max(self.Min, min(self.Max, p)))
        if int(self.nsided) > 0:
            print '8. signed char (80): %s' % struct.unpack('80s', infile.read(80))
            for i in range(0, int(self.nsided)):
                b = struct.unpack('f', infile.read(4))
                for bb in b:
                    p = bb * self.rho
                    self.nsided_p.append(max(self.Min, min(self.Max, p)))
        infile.close()
        
    def printTria3(self):
        for p in self.tria_p:
            print p
        
    def printQuad4(self):
        for p in self.quad_p:
            print p
                
    def printNsided(self):
        for p in self.nsided_p:
            print p

def readSurfaceFile(fileName):
    surf= []
    surfFile = open(fileName, 'r')
    for s in surfFile:
        surf.append(s.strip())
    surfFile.close()
    return surf
    
def readTimeData(fileName):
    tim = []
    timeFile = open(fileName, 'r')
    for t in timeFile:
        tim.append(t.strip())
    timeFile.close()
    return tim

def writeCaseFile(fileName, tim):
    caseFile = open(caseFileName,'w')
    caseFile.write("FORMAT\n")
    caseFile.write("type: ensight gold\n\n")
    caseFile.write("GEOMETRY\n")
    caseFile.write("model:  surface.geo\n\n")
    caseFile.write("VARIABLE\n")
    caseFile.write("scalar per element:            1       p               scal*****.p\n\n")
    caseFile.write("TIME\n")
    caseFile.write("time set:                      1\n")
    caseFile.write("number of steps:              " + str(len(tim)) + "\n")
    caseFile.write("filename start number:         0\n")
    caseFile.write("filename increment:            1\n")
    caseFile.write("time values:\n")
    for time in tim:
        caseFile.write(time+"\n")
    caseFile.close()

def getScalData(inGeoDir, inFileDir, t, surf, rho):
    sc = []
    for s in surf:
        inGeoFileName = os.path.join(inGeoDir, s+".geo")
        infileName = os.path.join(inFileDir, t)
        infileName = os.path.join(infileName, s+"_p")
        print "geo file:  " + inGeoFileName
        print "scal file: " + infileName
        p = Pressure(inGeoFileName, infileName, rho)
        p.readGeo()
        p.readP()
        sc.append(p)
    return sc

def writeScalData(fileName, scalar):
    outFile = open(fileName, 'w')
    outFile.write("scalar\n")
    n = 0
    for scal in scalar:
        n = n + 1
        outFile.write("part\n")
        outFile.write(str('{0:10d}'.format(n))+"\n")
        
        tria = scal.getTria3()
        quad = scal.getQuad4()
        nside = scal.getNsided()
        
        if tria > 0:
            outFile.write("tria3\n")
            for p in scal.getTriaP():
                outFile.write(str('{0:12.5e}'.format(p))+"\n")
        if quad > 0:
            outFile.write("quad4\n")
            for p in scal.getQuadP():
                outFile.write(str('{0:12.5e}'.format(p))+"\n")
        if nside > 0:
            outFile.write("nsided\n")
            for p in scal.getNsidedP():
                outFile.write(str('{0:12.5e}'.format(p))+"\n")  
    outFile.close()
    print "write file: " + outFileName                            


#--- main ---
homeDir = '/home2/tshimizu/ES/MMC_AERO/case4'
inGeoDir = os.path.join(homeDir, 'GEOM_ascii')
inFileDir = os.path.join(homeDir, 'surface')
outFileDir = os.path.join(homeDir, 'EnSight_surface')

rho = 1.205

surfFileName = os.path.join(homeDir, 'surf_list.dat')
surfaces = readSurfaceFile(surfFileName)

timeFileName = os.path.join(homeDir, 'time.dat')
times = readTimeData(timeFileName)

caseFileName = os.path.join(outFileDir,"surface.case")
writeCaseFile(caseFileName, times)


iters = 0

for time in times:
    scalars = getScalData(inGeoDir, inFileDir, time, surfaces, rho)
    print "numner of scalar = " + str(len(scalars))
    #--- output
    outFileName = os.path.join(outFileDir, "scal"+str(iters).zfill(5)+".p")
    print outFileName
    writeScalData(outFileName, scalars)
    iters = iters + 1

if __name__ == '__main__':
    pass