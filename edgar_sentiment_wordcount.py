


def write_document_sentiments(input_folder, output_file):
   
    import pandas as pd
    import os # needed to interate over files 
    import ref_data as edgar_data
    
    sentiment_dict = edgar_data.get_sentiment_word_dict()
    
    neg_words = set(sentiment_dict['Negative'])
    pos_words = set(sentiment_dict['Positive'])
    uncert_words = set(sentiment_dict['Uncertainty'])
    lit_words = set(sentiment_dict['Litigious'])
    const_words = set(sentiment_dict['Constraining'])
    modal_words = set(sentiment_dict['Strong_Modal'] + sentiment_dict['Weak_Modal'])
    

  

    tot_list_of_counts = []


    for files in os.listdir(input_folder):
    
        symbol_report_type = files.split('_')
        date = symbol_report_type[2].split('.')
        

        file = open(input_folder +'\\' + files, 'r')
        read_data = file.readlines()
        file.close()
        

        neg_count = 0 
        pos_count = 0 
        uncert_count = 0 
        lit_count = 0
        const_count = 0 
        modal_count = 0 

        list_of_counts = []


        for word in str(read_data).split():
            if word.upper() in neg_words:               # word.upper() to match with the dictionary word list format
                neg_count += 1
            elif word.upper() in pos_words:
                pos_count += 1
            elif word.upper() in uncert_words:
                uncert_count += 1
            elif word.upper() in lit_words:
                lit_count += 1
            elif word.upper() in const_words:
                const_count += 1
            elif word.upper() in modal_words:
                modal_count += 1
            

        list_of_counts.append(symbol_report_type[0].upper())
        list_of_counts.append(symbol_report_type[1])
        list_of_counts.append(date[0])
        list_of_counts.append(neg_count)
        list_of_counts.append(pos_count)
        list_of_counts.append(uncert_count)
        list_of_counts.append(lit_count)
        list_of_counts.append(const_count)
        list_of_counts.append(modal_count) 

        tot_list_of_counts.append(list_of_counts)
    

  

    df = pd.DataFrame(tot_list_of_counts, columns = ['Symbol', 'ReportType', 'FilingDate', 'Negative', 'Positive', 'Uncertainty', 'Litigious', 'Constraining', 'Modal'])


    df.to_csv(output_file, index = False)
    




