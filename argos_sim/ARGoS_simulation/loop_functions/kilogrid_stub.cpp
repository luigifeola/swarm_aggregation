//
// Created by Till Konrad Aust on 17.12.21.
//
// in case of simulation set flag
#define SIMULATION


#include "kilogrid_stub.h"

/*-----------------------------------------------------------------------------------------------*/
/* Initialization of the Loopfunctions.                                                          */
/*-----------------------------------------------------------------------------------------------*/
CKilogrid::CKilogrid():
CLoopFunctions() {}

CKilogrid::~CKilogrid() {}



/*-----------------------------------------------------------------------------------------------*/
/* Init method runs before every experiment starts.                                              */
/*-----------------------------------------------------------------------------------------------*/
void CKilogrid::Init(TConfigurationNode &t_tree) {
    // random tool for selecting messages and more
    m_pcRNG = CRandom::CreateRNG("argos");

    // get all Kilobots
    get_kilobots_entities();

    // read configuration - map and parameters
    read_configuration(t_tree);
    // run the setup message of the Kilogrid
    for(int x_it = 0; x_it < 10; x_it++){
        for(int y_it = 0; y_it < 20; y_it++){
            setup(x_it, y_it);
        }
    }

    // initialize some helpers to track the kilobots - only needed in sim
    robot_positions.resize(kilobot_entities.size());

    Reset();
    argos::LOG<<"Opening file"<<std::endl;
    outputFile.open("robot_positions.csv");
    argos::LOG<<"File opened ? "<<outputFile.is_open()<<std::endl;
    outputFile<<"timeStep,";
    for (size_t i = 0; i < kilobot_entities.size(); i++)
    {
      outputFile<<"robot_"<<i<<"_x,robot_"<<i<<"_y";
      if(i != kilobot_entities.size() - 1)
      {
        outputFile<<",";
      }
    }
    outputFile<<std::endl;
}


/*-----------------------------------------------------------------------------------------------*/
/* Gets called when the experiment is resetted.                                                  */
/*-----------------------------------------------------------------------------------------------*/
void CKilogrid::Reset() {
  timeStep = 0;
    /*
  * When the 'reset' method is called on the kilobot controller, the
  * kilobot state is destroyed and recreated. Thus, we need to
  * recreate the list of controllers and debugging info from scratch
  * as well.
  */
  m_tKBs.clear();
  /* Get the map of all kilobots from the space */
  CSpace::TMapPerType& tKBMap = GetSpace().GetEntitiesByType("kilobot");
  /* Go through them */
  for(CSpace::TMapPerType::iterator it = tKBMap.begin();
    it != tKBMap.end();
    ++it) {
   /* Create a pointer to the current kilobot */
   CKilobotEntity* pcKB = any_cast<CKilobotEntity*>(it->second);
   CCI_KilobotController* pcKBC = &dynamic_cast<CCI_KilobotController&>(pcKB->GetControllableEntity().GetController());
   /* Create debug info for controller */
   debug_info_t* ptDebugInfo = pcKBC->DebugInfoCreate<debug_info_t>();
   /* Append to list */
   m_tKBs.push_back(std::make_pair(pcKBC, ptDebugInfo));
  }
}


/*-----------------------------------------------------------------------------------------------*/
/* Gets called when the experiment ended.                                                        */
/*-----------------------------------------------------------------------------------------------*/
void CKilogrid::Destroy() {
    // TODO implement what should happen if simulation quits
}


/*-----------------------------------------------------------------------------------------------*/
/* Gets called before every simulation step.                                                     */
/*-----------------------------------------------------------------------------------------------*/
void CKilogrid::PreStep(){
  try{
  timeStep++;
  // LOG << "Time step : "<< timeStep<< std::endl;
    // collect all the data from the robots - and virtualize them
    virtual_message_reception();

    // run the loop
    if(timeStep%5 == 0) //kilogrid send messages every 0.5 seconds
    {
      for(int x_it = 0; x_it < 10; x_it++){
          for(int y_it = 0; y_it < 20; y_it++){
              loop(x_it, y_it);
          }
        }
    }
  }
  catch(std::exception& ex) {
      /* A fatal error occurred: dispose of data, print error and exit */
      LOGERR << ex.what() << std::endl;
#ifdef ARGOS_THREADSAFE_LOG
      LOG.Flush();
      LOGERR.Flush();
#endif
   }
}


/*-----------------------------------------------------------------------------------------------*/
/* Gets called after every simulation step.                                                      */
/*-----------------------------------------------------------------------------------------------*/
void CKilogrid::PostStep(){

 //  outputFile<<"timeStep,numberOfRobotsOnBlackSite,numberOfRobotsOnWhiteSite"<<std::endl;
 //
 //  int number_black = 0;
 //  int number_white = 0;
 //  /* Go through the kilobots */
 // for(size_t i = 0; i < m_tKBs.size(); ++i) {
 //    /* Create a pointer to the kilobot state */
 //    kilobot_state_t* ptState = m_tKBs[i].first->GetRobotState();
 //    int color = m_tKBs[i].second->ground_color_debug;
 //    if(color == 20)
 //    {
 //      number_black++;
 //    }
 //    else if(color == 21)
 //    {
 //      number_white++;
 //    }
 // }
 //
 // outputFile<<timeStep<<","<<number_black<<","<<number_white<<std::endl;
 // for(size_t i = 0; i < m_tKBs.size(); ++i) {
 //    /* Create a pointer to the kilobot state */
 //    kilobot_state_t* ptState = m_tKBs[i].first->GetRobotState();
 //    argos::LOG << m_tKBs[i].second->angle_debug << std::endl;
 //
 // }
 if(timeStep%10 == 0)
 {
   outputFile<<timeStep<<",";
   for(kilobot_entities_vector::iterator it = kilobot_entities.begin(); it != kilobot_entities.end(); it++)
   {
       CKilobotEntity *entity = *it;
       CVector2 position = GetKilobotPosition(*entity);
       //TODO implement writing in file the positions
       outputFile<<position.GetX()<<","<<position.GetY();
       if(it != kilobot_entities.end() - 1)
       {
         outputFile<<",";
       }
   }
   outputFile<<std::endl;
 }
}

/*-----------------------------------------------------------------------------------------------*/
/* This function reads the config file for the kilogrid and saves the content to configuration.  */
/*-----------------------------------------------------------------------------------------------*/
void CKilogrid::read_configuration(TConfigurationNode& t_node){
    // getting config script name from .argos file
    TConfigurationNode& tExperimentVariablesNode = GetNode(t_node,"variables");
    GetNodeAttribute(tExperimentVariablesNode, "config_file", config_file_name);

    // variables used for reading
    int tmp_x_module;
    int tmp_y_module;
    int tmp_value;
    int read_mode = 0; // 1 is address, 2 is data
    std::string tmp_str;

    // reading
    input.open(config_file_name);
    for( std::string line; getline( input, line ); ){
        // for each line
        if(!line.empty() && line[0] != '#'){  // exclude comments and empty lines

            //printf("%s\n",line.c_str()); // <- this way you can pring the line out!
            if (line == "address"){
                read_mode = 1;
            }else if(line == "data"){
                read_mode = 2;
            } else{
                // reading address
                if(read_mode == 1){
                    // isolating numbers
                    tmp_str = line;
                    tmp_str = tmp_str.substr(7);  // remove module
                    std::string::size_type p  = tmp_str.find('-');
                    tmp_y_module = std::stoi(tmp_str.substr(p+1));
                    tmp_x_module = std::stoi(tmp_str);
                }else if(read_mode == 2){ // read data
                    tmp_value = std::stoi(line, 0, 16);
                    configuration[tmp_x_module][tmp_y_module].push_back(tmp_value);
                }
            }
        }
    }
}


void CKilogrid::set_LED_with_brightness(int x, int y, cell_num_t cn, color_t color, brightness_t brightness){
    module_memory[x][y].cell_colour[cn] = color;
    GetSpace().GetFloorEntity().SetChanged();
}


/*-----------------------------------------------------------------------------------------------*/
/* Visualization of the floor color.                                                             */
/*-----------------------------------------------------------------------------------------------*/
CColor CKilogrid::GetFloorColor(const CVector2 &vec_position_on_plane) {
    int floor_color = position2option(vec_position_on_plane);

    // checks if the option is in time
    if(floor_color == 1){
        return CColor::RED;
    }else if(floor_color == 2){
        return CColor::BLUE;
    }else if(floor_color == 3){
        return CColor::WHITE;
    }else if(floor_color == 4){
        return CColor::BLACK;
    }

    return CColor::GREEN; //to visually debug
}


/*-----------------------------------------------------------------------------------------------*/
/* Returns the Option of the given position.                                                     */
/*-----------------------------------------------------------------------------------------------*/
UInt16 CKilogrid::position2option(CVector2 t_position){
    int module_x = t_position.GetX()*10;
    int module_y = t_position.GetY()*10;

    uint8_t cell = 0;
    int x = t_position.GetX()*20;
    int y = t_position.GetY()*20;

    if (x >= 20) x = 19;
    if (y >= 40) y = 39;
    if (x < 0) x = 0;
    if (y < 0) y = 0;

    // get the cell
    if(x % 2 == 0 && y % 2 == 1){
        cell = 0;
    }else if(x % 2 == 1 && y % 2 == 1){
        cell = 1;
    }else if(x % 2 == 0 && y % 2 == 0){
        cell = 2;
    }else if(x % 2 == 1 && y % 2 == 0){
        cell = 3;
    }

    return module_memory[module_x][module_y].cell_colour[cell];
}


CVector2 CKilogrid::position2cell(CVector2 t_position){
    int x = t_position.GetX()*20;
    int y = t_position.GetY()*20;

    if (x >= 20) x = 19;
    if (y >= 40) y = 39;
    if (x < 0) x = 0;
    if (y < 0) y = 0;

    return CVector2(x,y);
}


CVector2 CKilogrid::position2module(CVector2 t_position) {
    float x = t_position.GetX() * 10;
    float y = t_position.GetY() * 10;

    if (x >= 10) x = 9;
    if (y >= 20) y = 19;
    if (x < 0) x = 0;
    if (y < 0) y = 0;

    return CVector2(int(x),int(y));
}


CVector2 CKilogrid::module2cell(CVector2 module_pos, cell_num_t cn){
    int cur_x = module_pos.GetX() * 2;
    int cur_y = module_pos.GetY() * 2;

    switch(cn){
        case 0:
            cur_y += 1;
            break;
        case 1:
            cur_x += 1;
            cur_y += 1;
            break;
        case 2:
            break;
        case 3:
            cur_x += 1;
    }

    return CVector2(cur_x, cur_y);
}


void CKilogrid::get_kilobots_entities(){
    // Get the map of all kilobots from the space
    CSpace::TMapPerType& mapKilobots=GetSpace().GetEntitiesByType("kilobot");
    // Go through them
    for(CSpace::TMapPerType::iterator it = mapKilobots.begin();it != mapKilobots.end();++it) {
        kilobot_entities.push_back(any_cast<CKilobotEntity*>(it->second));
    }
}


/*-----------------------------------------------------------------------------------------------*/
/* Returns the position of the kilobot.                                                          */
/*-----------------------------------------------------------------------------------------------*/
CVector2 CKilogrid::GetKilobotPosition(CKilobotEntity& c_kilobot_entity){
    CVector2 vecKP(c_kilobot_entity.GetEmbodiedEntity().GetOriginAnchor().Position.GetX(),
                   c_kilobot_entity.GetEmbodiedEntity().GetOriginAnchor().Position.GetY());
    return vecKP;
}


/*-----------------------------------------------------------------------------------------------*/
/* Returns the id of the kilobot.                                                                */
/*-----------------------------------------------------------------------------------------------*/
// UInt16 CKilogrid::GetKilobotId(CKilobotEntity& c_kilobot_entity){
//     std::string strKilobotID((c_kilobot_entity).GetControllableEntity().GetController().GetId());
//     std::string newId = "";
//     for (char c : strKilobotID)
//       if(std::isdigit(c))
//         newId = newId + c;
//
//     return std::stoul(newId);
// }

void CKilogrid::virtual_message_reception(){
    // get position information, later used for sending stuff!!
    // try{
      for(kilobot_entities_vector::iterator it = kilobot_entities.begin(); it != kilobot_entities.end(); it++)
      {
          // LOG << "kilobot_entities size " << kilobot_entities.size() << std::endl;
          // LOG << "robot_positions size " << robot_positions.size() << std::endl;
          CKilobotEntity *entity = *it;
          // UInt16 id = GetKilobotId(*entity);
          CVector2 position = GetKilobotPosition(*entity);
          // LOG << "id used " << id << std::endl;
          robot_positions.at(it - kilobot_entities.begin()) = position2cell(position);
      }
    // }
    // catch(...){
    //   LOG << "crashing in virtual_message_reception" << std::endl;
    // }
}


void CKilogrid::set_IR_message(int x, int y, IR_message_t &m, cell_num_t cn) {
  // try{
      // get correct cell
      CVector2 cell_pos = module2cell(CVector2(x,y), cn);

      // get kilobots on this cell
      kilobot_entities_vector current_robots;

      // LOG << "before accessing robot_positions" << std::endl;
      for(uint8_t it=0;it < kilobot_entities.size();it++)
      {
          if(robot_positions[it].GetX() == cell_pos.GetX() && robot_positions[it].GetY() == cell_pos.GetY())
          {
              current_robots.push_back(kilobot_entities[it]);
          }
      }
      // LOG << "after accessing robot_positions" << std::endl;

      // LOG << "before sending IR_message" << std::endl;
      // send to all kilobots on this cell
      for(UInt16 it=0; it < current_robots.size(); it++){
          message_t message_to_send;
          message_to_send.type = m.type;
          message_to_send.data[0] = m.data[0];
          message_to_send.data[1] = m.data[1];
          message_to_send.data[2] = m.data[2];
          message_to_send.data[3] = m.data[3];
          message_to_send.data[4] = m.data[4];
          message_to_send.data[5] = m.data[5];
          message_to_send.data[6] = m.data[6];
          message_to_send.data[7] = m.data[7];
          GetSimulator().GetMedium<CKilobotCommunicationMedium>("kilocomm").SendOHCMessageTo(*current_robots[it], &message_to_send);
      }
      // LOG << "after sending IR_message" << std::endl;
    // }
    // catch(...){
    //   LOG << "crashing in set_IR_message" << std::endl;
    // }
}

/*-----------------------------------------------------------------------------------------------*/
/* The following methods need to be implemented by the user - they aim to be such as the         */
/* methods used on the real Kilogrid.                                                            */
/*-----------------------------------------------------------------------------------------------*/
void CKilogrid::setup(int x, int y){
    module_memory[x][y].cell_colour[0] = color_t (configuration[x][y][0]);
    module_memory[x][y].cell_colour[1] = color_t (configuration[x][y][1]);
    module_memory[x][y].cell_colour[2] = color_t (configuration[x][y][2]);
    module_memory[x][y].cell_colour[3] = color_t (configuration[x][y][3]);
}


void CKilogrid::loop(int x, int y){
  for(int i = 0; i < 4; ++i){
    switch(module_memory[x][y].cell_colour[i]){
        case 1:
            set_LED_with_brightness(x, y, cell_id[i], module_memory[x][y].cell_colour[i], HIGH);
            module_memory[x][y].ir_message_tx->type = 1;
            module_memory[x][y].ir_message_tx->data[0] = 22; //grey colour
            module_memory[x][y].ir_message_tx->data[1] = 1; //obstacle true
            set_IR_message(x, y, *module_memory[x][y].ir_message_tx, cell_id[i]);
            break;
        case 2:
            set_LED_with_brightness(x, y, cell_id[i], module_memory[x][y].cell_colour[i], HIGH);
            module_memory[x][y].ir_message_tx->type = 1;
            module_memory[x][y].ir_message_tx->data[0] = 22; //grey colour
            module_memory[x][y].ir_message_tx->data[1] = 0; //obstacle false
            set_IR_message(x, y, *module_memory[x][y].ir_message_tx, cell_id[i]);
            break;
        case 3:
            set_LED_with_brightness(x, y, cell_id[i], module_memory[x][y].cell_colour[i], HIGH);
            module_memory[x][y].ir_message_tx->type = 1;
            module_memory[x][y].ir_message_tx->data[0] = 21; //white colour
            module_memory[x][y].ir_message_tx->data[1] = 0; //obstacle false
            set_IR_message(x, y, *module_memory[x][y].ir_message_tx, cell_id[i]);
            break;
        case 4:
            set_LED_with_brightness(x, y, cell_id[i], module_memory[x][y].cell_colour[i], HIGH);
            module_memory[x][y].ir_message_tx->type = 1;
            module_memory[x][y].ir_message_tx->data[0] = 20; //black colour
            module_memory[x][y].ir_message_tx->data[1] = 0; //obstacle false
            set_IR_message(x, y, *module_memory[x][y].ir_message_tx, cell_id[i]);
            break;
        default:
            break;
       }
	}
}

REGISTER_LOOP_FUNCTIONS(CKilogrid, "kilogrid_loop_functions")
