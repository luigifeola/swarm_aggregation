#include "kilolib.h"
#include "agent.h"
#include <stdlib.h>
#include <math.h>
// #include <stdio.h>
// #include <stdlib.h>
// #include <float.h>
#include <debug.h>

// #include "utils.h"
// #include "kilo_rand_lib.h"
// #include "kilob_tracking.h"
// #include "kilob_messaging.h"

//PI
#define PI 3.14159265359
#define RAND_MAX_VALUE 255

typedef enum{
    false = 0,
    true = 1,
} bool;

struct broadcasting_robot_info{
  uint16_t id;
};

uint32_t timer_go_straight = 0;
uint32_t timer_turn = 0;
double timer_turn_coefficient = 45; //coefficient use to convert from turning angle to time turning

bool broadcast_bool = false;
uint32_t neighbors_sampling_duration = 32*2; //2 seconds sampling
uint32_t neighbors_sampling_timer = 0;
int buffer_size = 25;
struct broadcasting_robot_info broadcasting_robots[25];

double alpha = 1;
double beta = 0.75;

double crw_factor = 0; //between 0 and 1
double levy_factor = 2; //between 0 and 2
double exp_factor = 1;
double thetas[360];
double crw_weights[360];
int max_levy_steps = 100;
double levy_weights[100];

int ground_color = 0;
bool obstacle = false;
bool wall_avoidance_activated = 0;

int stay_factor = 1;

message_t msg; //msg to send

double uniform_distribution(double a, double b)
{
  return ((double) rand_hard() * (b - a) + a) / ((double)RAND_MAX_VALUE + 1);
}

void crw_pdf()
{
  for (size_t i = 0; i < 359; i++)
  {
    double num = (1 - pow(crw_factor,2));
    double denom = 2 * PI * (1 + pow(crw_factor,2) - 2 * crw_factor * cos(thetas[i] * PI / 180));
    double f =1;
    if(denom != 0)
    {
      f = num / denom;
    }
    crw_weights[i] = f;
  }
  return;
}

void levy_pdf()
{
  for (size_t i = 1; i < max_levy_steps + 1; i++)
  {
    levy_weights[i-1] = pow((double) i,(-levy_factor - 1));
  }
}

double binary_search(double a[], int a_size, double item)
{
    int first = 0;
    int last = a_size - 1;
    int mid = 0;
    do
    {
        mid = first + (last - first) / 2;
        if (item > a[mid])
            first = mid + 1;
        else
            last = mid - 1;
        if (a[mid] == item)
            return mid;
    } while (first <= last);
    return mid;
}

double choices(double array[], double weights[], int array_size)
{
  double cum_weights[array_size];
  double cum_sum = 0;
  for (size_t i = 0; i < array_size; i++)
  {
    cum_sum += weights[i];
    cum_weights[i] = cum_sum;
  }
  double random_number = uniform_distribution(cum_weights[0], cum_weights[array_size - 1]);
  int pos = binary_search(cum_weights, array_size, random_number);
  return array[pos];
}

void broadcast()
{
  broadcast_bool = true;
}

void stop_broadcast()
{
  broadcast_bool = false;
}

message_t *message_tx()
{
  if(broadcast_bool == true)
  {
    return &msg;
  }
  else
  {
    return NULL;
  }
}

void message_rx(message_t *message, distance_measurement_t *distance)
{
	if (message->type == 1) //type 1 for message received from the Modules
	{
    ground_color = message->data[0];
		obstacle = message->data[1];
    // debug_info_set(ground_color_debug, ground_color);
  }
  if (message->type == 2) //type 2 for message received from the Kilobots
	{
    uint16_t id = message->data[0];
    for(int i = 0; i < buffer_size; ++i)
    {
      if(broadcasting_robots[i].id == id)
      {
        return;
      }
    }
    for(int i = 0; i < buffer_size; ++i)
    {
      if(broadcasting_robots[i].id == 0)
      {
        broadcasting_robots[i].id = id;
        return;
      }
    }
  }
  return;
}

void setup() {
  for(int i = 0; i < buffer_size; ++i)
  {
      broadcasting_robots[i].id = 0;
  }
  for (size_t i = 0; i < 359; i++)
  {
    thetas[i] = i;
  }
  //from factors calculate weights
  crw_pdf();
  levy_pdf();
	// kilob_tracking_init(); //no need for kilob_messaging_init, it calls it with this
	// init_motors();
  msg.type = 2;
  msg.data[0] = kilo_uid;
  msg.crc = message_crc(&msg);
  broadcast();

  neighbors_sampling_timer = neighbors_sampling_duration;
}

void loop() {
    // debug_info_set(kilo_ticks_debug, kilo_ticks);
    // debug_info_set(timer_go_straight_debug, timer_go_straight);

    if(neighbors_sampling_timer <= kilo_ticks)
    {
      //implement neighbors count with update_rate
      double neighbors_count = 0;
      for(int i = 0; i < buffer_size; ++i)
      {
        if(broadcasting_robots[i].id != 0)
        {
          neighbors_count = neighbors_count + 1;
        }
        broadcasting_robots[i].id = 0;
      }

      //update of the behavior (the factors)
      exp_factor = alpha * exp(-beta * neighbors_count);
      crw_factor = 0.9 * exp_factor;
      levy_factor = 2 - 1.9 * exp_factor;

      //stay ?
      double uniform_number = uniform_distribution(0,1);
      if(uniform_number >= exp_factor)
      {
        stay_factor = 0;
      }
      else
      {
        stay_factor = 1;
      }

      //from factors calculate weights
      crw_pdf();
      levy_pdf();
      neighbors_sampling_timer = kilo_ticks + neighbors_sampling_duration;
    }

    //movement
    if(obstacle == 1 && wall_avoidance_activated == 0)
    {
      wall_avoidance_activated = 1;
      timer_turn = 0;
      timer_go_straight = 0;
    }
    if(wall_avoidance_activated == 1)
    {
      //wall avoidance behavior
      set_color(RGB(3, 0, 0));
      if(timer_turn == 0 && timer_go_straight == 0)
      {
        set_motors(kilo_turn_left, 0);
        double time = 180 / timer_turn_coefficient; //turn 90 degrees
        double double_time = time * 32;
        uint32_t int_time = double_time;
        timer_turn = kilo_ticks + int_time;
      }
      else if(timer_turn <= kilo_ticks && timer_go_straight == 0)
      {
        timer_turn = 0;
        set_motors(kilo_straight_left, kilo_straight_right);
        timer_go_straight = kilo_ticks + 32*10;
      }
      else if(timer_go_straight <= kilo_ticks && timer_turn == 0)
      {
        timer_go_straight = 32*4;
        wall_avoidance_activated = 0;
      }
    }
    else
    {
      //normal random walk behavior
      if(timer_go_straight <= kilo_ticks && timer_turn == 0)
      {
        set_color(RGB(0, 3, 0));
        //end of step, implement turning here (take an angle from the weights with choices and set motors)
        double angle = choices(thetas, crw_weights, 360);
        if(angle >= 180)
        {
          angle = 360 - angle;
          set_motors(kilo_turn_left * stay_factor, 0);
        }
        else
        {
          set_motors(0, kilo_turn_right * stay_factor);
        }
        double time = angle / timer_turn_coefficient;
        double double_time = time * 32;
        uint32_t int_time = double_time;
        timer_turn = kilo_ticks + int_time;
        timer_go_straight = 0;
      }
      else if(timer_turn <= kilo_ticks && timer_go_straight == 0)
      {
        set_color(RGB(0, 0, 3));
        //end of turn, implement the step here (take an angle from the weights with choices and set motors)
        double levy_steps[max_levy_steps];
        for (size_t i = 0; i < max_levy_steps; i++)
        {
          levy_steps[i] = (double) i + 1.0;
        }
        double step = choices(levy_steps, levy_weights, max_levy_steps);
        timer_go_straight = kilo_ticks + (uint32_t) step * 8;
        set_motors(kilo_straight_left * stay_factor, kilo_straight_right * stay_factor);
        timer_turn = 0;
      }
    }
  //if needed, add stuff with tracking data here
}

int main() {
  kilo_init();
	// utils_init();
  kilo_message_tx = message_tx;
	kilo_message_rx = message_rx; // register IR reception callback

  debug_info_create();

  kilo_start(setup, loop);

  return 0;
}
