import pandas as pd
import numpy as np
import os.path
import nltk
#nltk.download('averaged_perceptron_tagger')
from nltk.tag.perceptron import PerceptronTagger


lists_path = '../Lists/'
'''
A dictionary that stores the one-on-one correspondence between 321 gender specific
words/phrases and whether they indicate male or female. 1 stands for male and -1 stands for
female. The classification of the gender specific worsd are from the following three lists:

1. Gender in English: Masculine and Feminine Words, ilu English:
http://www.iluenglish.com/gender-in-english-masculine-and-feminine-words/

2. Stjerneskinn.com: http://stjerneskinn.com/gender-neutral-words.htm

3. EXAMPLES OF GENDER-SENSITIVE LANGUAGE: 
http://www.servicegrowth.net/documents/Examples%20of%20Gender-Sensitive%20Language.net.pdf
'''

'''
Read words from two lists, separately a list of male words and a list of female words -
female_list and a list of male words - male_list. For a word in male_list, the value
associated with it in the dictionary is 1 and for a word in female_list, the value
associated in the dictionary is -1.
'''
gender_dictionary = {}
male_list = open(lists_path+'male_list.txt', 'r')
female_list = open(lists_path+'female_list.txt', 'r')

for word in male_list:
    male_key = word.rstrip('\n')
    gender_dictionary[male_key] = 1

for word in female_list:
    female_key = word.rstrip('\n')
    gender_dictionary[female_key] = -1

male_list.close()
female_list.close()


def G(word):
    '''
    A function that accepts a string as an argument and returns the gender associated with 
    the string.

    Args
    ----
    word - a str

    Returns
    -------
    1  - if the word is in gender_dictionary and gender_dictionary[word] = 1
    -1 - if the word is in gender_dictionary and gender_dictioanry[word] = -1
    0  - if the word is not in gender_dictionary
    '''
    return gender_dictionary.get(word, 0)



def get_audio_feature(path,year,filename,whole_list):
    # for ABA format
    # path indicate the root direction for the whole data
    # filename represents .csv file for aba
    # return an n*23 matrix contains speaker infomation, audio features and classify
    audio_matrix = np.empty((0,23))
    aba_table_info = pd.read_csv(data_dir+"ABA/aba_table_info.csv")
    filepath = path+"FAVE/FAVE-extract/"+str(year)+"_vowels/ABA/"+str(filename)+".csv"
    #print path+"FAVE/FAVE-extract/"+str(year)+"_vowels/ABA/"+str(filename)+".csv"
    if os.path.isfile(filepath)==False:
        return
    else:
        print (path+"FAVE/FAVE-extract/"+str(year)+"_vowels/ABA/"+str(filename)+".csv")
    feature_list = pd.read_csv(path+"FAVE/FAVE-extract/"+str(year)+"_vowels/ABA/"+str(filename)+".csv")
    row_num = feature_list.shape[0]#all word extracted from the get_audio_feature
    if row_num == 0:
        return
    #fpr de-mean purpose
    id_tmp = 0
    docket_id = 0
    # Create an empty dataframe
    df = pd.DataFrame()

    index = 0.0
    number_m = 0.0;
    gender_word_male = {};
    number_w = 0.0;
    gender_word_female = {};
    print("Total rows: %i" %(row_num))
    while (index < row_num):
        if (index%1000 == 0):
            print("Index: %i" %(index))
        speak_a_id = feature_list["speakerA1_id"][index]#speaker A correspond to aba_table_info.csv
        speak_b_id = feature_list["speakerB_id"][index]#speaker B
        tier_num = feature_list["tiernum"][index]#decide who is speaking, correspond to textgrid file
        dt_row = whole_list[(whole_list['TextGrid'] == filename+".TextGrid")&(whole_list["TierNumber"]==tier_num)].index
        speaker_pattern = []
        if len(dt_row) > 0:
            speaker = whole_list["TierName"][dt_row].tolist()
            speakers = speaker[0].split(" ")
            for s in speakers:
                s_tmp = list(s)
                s_tmp[0] = s_tmp[0].upper()
                s = "".join(s_tmp)
                speaker_pattern.append(s)

        pattern = "|".join(speaker_pattern)
        text = feature_list["word"][index]#text, specific words
        pretrain = PerceptronTagger()
        identity_for_text = pretrain.tag([text])
        #filter
        if (identity_for_text[0][1]=='NN' or identity_for_text[0][1] =='NNS'):
            classify = G(text.lower());
            if classify == 1:
                value = gender_word_male.get(text, -1)
                if value != -1:
                    gender_word_male[text] += 1
                else:
                    gender_word_male[text] = 1
                number_m += 1
            if classify == -1:
                value = gender_word_female.get(text, -1)
                if value!=-1:
                    gender_word_female[text] += 1
                else:
                    gender_word_female[text] = 1
                number_w += 1

            text_feature_f1 = feature_list["F1"][index]
            text_feature_f2 = feature_list["F2"][index]
            text_feature_f3 = feature_list["F3"][index]
            text_feature_B1 = feature_list["B1"][index]
            text_feature_B2 = feature_list["B2"][index]
            text_feature_B3 = feature_list["B3"][index]
            text_feature_t = feature_list["t"][index]
            text_feature_beg = feature_list["beg"][index]
            text_feature_end = feature_list["end"][index]
            text_feature_dur = feature_list["dur"][index]
            text_feature_F120 = feature_list["F1@20%"][index]
            text_feature_F220 = feature_list["F2@20%"][index]
            text_feature_F135 = feature_list["F1@35%"][index]
            text_feature_F235 = feature_list["F2@35%"][index]
            text_feature_F150 = feature_list["F1@50%"][index]
            text_feature_F250 = feature_list["F2@50%"][index]
            text_feature_F160 = feature_list["F1@65%"][index]
            text_feature_F260 = feature_list["F2@65%"][index]
            text_feature_F180 = feature_list["F1@80%"][index]
            text_feature_F280 = feature_list["F2@80%"][index]

            dt_row_tmp = aba_table_info[(aba_table_info["docket_id"]==filename)&(aba_table_info["speakerA"].str.contains(pattern,na=False))].index
            dt_row_2 = dt_row_tmp.tolist()
            if len(dt_row_2) != 0:
                #find speaker id
                #save validated data
                speaker_id = aba_table_info["speakerA_id"][dt_row_2[0]]
                tmp_data = np.array([filename,speaker_id,text_feature_f1,text_feature_f2,text_feature_f3,text_feature_B1,
                    text_feature_B2,text_feature_B3,text_feature_t,text_feature_beg,text_feature_end,text_feature_dur,
                    text_feature_F120,text_feature_F220,text_feature_F135,text_feature_F235,text_feature_F150,text_feature_F250,
                    text_feature_F160,text_feature_F260,text_feature_F180,text_feature_F280,classify,identity_for_text[0][1],text]).reshape(1,25)
                test_data_tmp = pd.DataFrame(tmp_data,columns=['docket_id','speaker_id','f1','f2','f3','B1','B2','B3','t','beg','end','dur',
                    'f1@20%','f2@20%','f1@35%','f2@35%','f1@50%','f2@50%','f1@60%','f2@60%','f1@80%','f2@80%', 'classify', 'identity','text'])
                test_data_tmp[['f1@20%','f2@20%','f1@35%','f2@35%','f1@50%','f2@50%','f1@60%','f2@60%','f1@80%','f2@80%']] = test_data_tmp[['f1@20%','f2@20%','f1@35%','f2@35%','f1@50%','f2@50%','f1@60%','f2@60%','f1@80%','f2@80%']].apply(pd.to_numeric,errors='coerce')
                df = df.append(test_data_tmp,ignore_index=True)
            #print tmp_data.shape
            #audio_matrix = np.append(audio_matrix,tmp_data,axis = 0)
        index += 1
    #deal with the last person in this speech
    # de-mean
    id_tmp = 0
    docket_id_tmp = 0
    if df.shape[0]!=0:
    # not empty
    # define new column
        new_colom_f1_20 = pd.Series(np.zeros(df.shape[0]), index=df.index)
        new_colom_f1_35 = pd.Series(np.zeros(df.shape[0]), index=df.index)
        new_colom_f1_50 = pd.Series(np.zeros(df.shape[0]), index=df.index)
        new_colom_f1_60 = pd.Series(np.zeros(df.shape[0]), index=df.index)
        new_colom_f1_80 = pd.Series(np.zeros(df.shape[0]), index=df.index)
        new_colom_f2_20 = pd.Series(np.zeros(df.shape[0]), index=df.index)
        new_colom_f2_35 = pd.Series(np.zeros(df.shape[0]), index=df.index)
        new_colom_f2_50 = pd.Series(np.zeros(df.shape[0]), index=df.index)
        new_colom_f2_60 = pd.Series(np.zeros(df.shape[0]), index=df.index)
        new_colom_f2_80 = pd.Series(np.zeros(df.shape[0]), index=df.index)
        for i_new in range(df.shape[0]):
            df_group = df[(df['speaker_id']==df['speaker_id'][i_new])].mean()
            #print "Find column: ", df['f1@20%']
            #print "Mean: ",df[(df['speaker_id'] == df['speaker_id'][i_new])&(df['docket_id']==df['docket_id'][i_new])]["f1@20%"].mean()
            new_colom_f1_20[i_new] = df['f1@20%'][i_new]- df_group['f1@20%']
            new_colom_f1_35[i_new] = df['f1@35%'][i_new]- df_group['f1@35%']
            new_colom_f1_50[i_new] = df['f1@50%'][i_new]- df_group['f1@50%']
            new_colom_f1_60[i_new] = df['f1@60%'][i_new]- df_group['f1@60%']
            new_colom_f1_80[i_new] = df['f1@80%'][i_new]- df_group['f1@80%']
            new_colom_f2_20[i_new] = df['f2@20%'][i_new]- df_group['f2@20%']
            new_colom_f2_35[i_new] = df['f2@35%'][i_new]- df_group['f2@35%']
            new_colom_f2_50[i_new] = df['f2@50%'][i_new]- df_group['f2@50%']
            new_colom_f2_60[i_new] = df['f2@60%'][i_new]- df_group['f2@60%']
            new_colom_f2_80[i_new] = df['f2@80%'][i_new]- df_group['f2@80%']

        # add new column
        df['f1@20%_c'] = new_colom_f1_20
        df['f1@35%_c'] = new_colom_f1_35
        df['f1@50%_c'] = new_colom_f1_50
        df['f1@60%_c'] = new_colom_f1_60
        df['f1@80%_c'] = new_colom_f1_80
        df['f2@20%_c'] = new_colom_f2_20
        df['f2@35%_c'] = new_colom_f2_35
        df['f2@50%_c'] = new_colom_f2_50
        df['f2@60%_c'] = new_colom_f2_60
        df['f2@80%_c'] = new_colom_f2_80
        # save or add these column into the audio_feature.csv file
        output_dir = '../Data/Outputs/'
        file_name = 'audio_feature_'+str(year)+'.csv'
        if not os.path.isfile(output_dir+file_name):
            df.to_csv(output_dir+file_name,header ='column_names',index = False)
        else:
            df.to_csv(output_dir+file_name,mode = 'a',header=False,index = False)

    print ("total number of words: ",row_num)
    print ("For male: ",number_m,gender_word_male)
    print ("percentage for label as male:",number_m/row_num)
    print ("For female: ",number_w,gender_word_female)
    print ("percentage for label as female:",number_w/row_num)
    print ("")
    return



def get_start(path):
    whole_list = pd.read_csv(path+"oyez_full/fullTierName_1998.csv")
    #start point
    index = 0
    #row_num = whole_list.shape[0]
    row_num = whole_list.shape[0]
    tmp = 1
    text_grid = 0#text_grid for
    year = 0
    tier_dictionary={}
    print("Outer Loop - Total Rows: %i" %(row_num))
    while(index < row_num):
        if (index%100 == 0):
            print("Outer Loop - Index: %i" %(index))
        if whole_list["useable"][index]==1:
            #indicate a new file
            if tmp != whole_list["TextGrid"][index]:
                tmp = whole_list["TextGrid"][index]
                year = whole_list["Year"][index]
                get_audio_feature(path,year,whole_list["TextGrid"][index].split(".")[0],whole_list)
        index += 1



if __name__ == '__main__':
    data_dir = '../Data/Inputs/'
    get_start(data_dir)

