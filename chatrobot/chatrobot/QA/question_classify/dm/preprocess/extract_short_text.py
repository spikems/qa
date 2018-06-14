#encoding:utf-8

class ExtractShortText:

    def __init__(self):
        pass

    def findPosition(self, target, sContext):
        lPosition = []
        if target.strip() == '':
            target = '#####!!!!!!$$$!!##!fdasjkd!@@@@@@@@'
	pos = sContext.find(target)
	before = 0
	while pos != -1:
	    lPosition.append((pos + before, pos + before + len(target)))
	    sContext = sContext[pos + len(target) :]
	    before = pos + before + len(target)
	    pos = sContext.find(target)
	return lPosition

    def extract_short_text(self, sTarget, sContext, iRange = 100):

        '''
            abstract nearby text from raw paper
            ret:
                unicode string : short text 
        '''
        sTarget = sTarget if type(sTarget) == unicode else sTarget.decode('utf-8', 'ignore')
        sContext = sContext if type(sContext) == unicode else sContext.decode('utf-8', 'ignore')
 
        iLength = len(sContext)
        iBrand = 0
        jBrand = 0
        lBrandGap = []
        isFirst = True
        lPosition = self.findPosition(sTarget, sContext)
        for tPosition in lPosition:
    	    if isFirst:
                iBrand = tPosition[0]
                jBrand = tPosition[1]
                isFirst = False
            else:
                lBrandGap.append([jBrand, tPosition[0], (tPosition[0] - jBrand)])
                jBrand = tPosition[1]
        sText = ''
        for iGs, iGe, iGap in lBrandGap:
            if iGap > iRange * 2:
                iBeg = 0 if (iBrand - iRange < 0) else iBrand - iRange
                iEnd = iGs + iRange
                sText = u"%s 。 %s" % (sText, sContext[iBeg : iEnd])
                iBrand = iGe

        iBeg = 0 if (iBrand - iRange < 0) else iBrand - iRange
        iEnd = jBrand + iRange
        sText = u"%s 。 %s" % (sText, sContext[iBeg : iEnd])
        return sText

if __name__ == '__main__':
    target = '铜锣湾'
    text = '在铜锣湾的旗舰店、8铜锣湾貌似不需要预约也能拿到现货。铜锣湾iPhone7的128G是5588港币，约4764元人民币。'
    iRange = 101
    text0 = ExtractShortText().extract_short_text(target, text, iRange )
    print text0
