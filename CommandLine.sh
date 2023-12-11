
#!/bin/bash

# Question 1: What is the most-watched Netflix title?

cat /home/matt/Documenti/ADM/HMW_4/vodclickstream_uk_movies_03.csv | awk -F, '{if ($2>0) duration[$(NF-1)]+=$3; title[$(NF-1)] = $4;}END{for(i in duration) print "MOVIE_TITLE: " title[i]", " int(duration[i]/3600) " hours of watchtime";}' vodclickstream_uk_movies_03.csv | sort -t, -k2 -nr | head -n 1

#cat "file path" is used to read the cvs file, and -F is used to specify the field separator (in this case, the comma).
#Select the positive durations [{$2>0}] and sum the values (as we can see in the first curly brackets code block).
#Then for every i in duration we print the title of the movie and the total watchtime.
#(NF-1) is used to select the second-to-last column, since NF stands for number of fields in a row, for each row.
#Finally, we sort the elements in descending order with (sort -t, -k2 -nr) and select the first row (head -n 1). 
#The result is the most watched movie on Netflix.


#Question 2: Report the average time between subsequent clicks on Netflix.com

cat /home/matt/Documenti/ADM/HMW_4/vodclickstream_uk_movies_03.csv | sort -t, -k2,2 -k3,3  vodclickstream_uk_movies_03.csv | head -n -1 > sorted_vodclickstream_uk_movies_03.csv

#sort the datetime column with (sort -t, -k2,2 -k3,3) so that we have the lower year,month,day and time as first element
#and save the result in a new file, sorted_vodclickstream_uk_movies_03.csv

cat /home/matt/Documenti/ADM/HMW_4/sorted_vodclickstream_uk_movies_03.csv | awk -F, '{
    if (NR==1) {prev_time = $2; next} 
    curr_time = $2; 
    gsub(/[-:]/," ",curr_time); 
    gsub(/[-:]/," ",prev_time);  
    diff = int((mktime(curr_time) - mktime(prev_time)));
    if (diff >= 0) {totalc += diff;}
    else {totalc += 86400+diff;}
    prev_time = curr_time
}END{print "THE AVERAGE TIME BETWEEN SUBSEQUENT CLICKS ON THE PLATFORM IS: " int((totalc)/(671735)) " SECONDS";}' /home/matt/Documenti/ADM/HMW_4/sorted_vodclickstream_uk_movies_03.csv

#"cat" the sorted file and use awk to calculate the difference between the current time and the previous time with mktime.
#Use gsub to substitute the "-" and ":" with a space, so that we can use mktime.
#Use NR==1 to skip the first row, since we don't have a previous time to compare it to.
#Use diff >= 0 to check if the difference is positive, and if it is we add it to the totalc.
#Use diff < 0 to check if the difference is negative, and if it is we add it to the totalc
#With 86400 seconds (24 hours). Without this, we would have an erroneous time difference (e.g 23:59 and 00:02 
#of the next day are 3 minutes apart, but mktime is going to print 23 hours and 57 minutes).
#We finally print the average time between subsequent clicks on the platform, which is the totalc divided by the number of rows.



# Question 3: Provide the ID of the user that has spent the most time on Netflix


cat /home/matt/Documenti/ADM/HMW_4/vodclickstream_uk_movies_03.csv | awk -F, '{if ($2>0) duration[$(NF)]+=$3; id[$(NF)] = $NF;}END{for(i in duration) print "USER_ID: " id[i]", " int(duration[i]/3600) " hours of watchtime";}' vodclickstream_uk_movies_03.csv | sort -t, -k2 -nr | head -n 1

#same as question 1, but we select the last column (NF) instead of the second-to-last (NF-1), which contains the user_id.

