#include <chrono>
#include <thread>

int main() {
    auto t = std::chrono::system_clock::now();
    while(true){
	    time_t current_time;
	    tm* current_tm;
	    char current_timer_str[256];

        time(&current_time);
	    current_tm = localtime(&current_time);
	    strftime(current_timer_str, sizeof(current_timer_str), "%Y-%m-%d %H:%M:%S", current_tm);


        fprintf(stdout, "%s\n", current_timer_str);
        
        if(current_tm->tm_sec == 13)
            fprintf(stderr, "On ho!\n");

        fflush(stderr);
        fflush(stdout);

        t = t + std::chrono::seconds(1);
        std::this_thread::sleep_until(t);
    }
    return 0;
}
