/* USER CODE BEGIN Header */
/**
  ******************************************************************************
  * @file           : main.c
  * @brief          : Main program body
  ******************************************************************************
  * @attention
  *
  * <h2><center>&copy; Copyright (c) 2021 STMicroelectronics.
  * All rights reserved.</center></h2>
  *
  * This software component is licensed by ST under BSD 3-Clause license,
  * the "License"; You may not use this file except in compliance with the
  * License. You may obtain a copy of the License at:
  *                        opensource.org/licenses/BSD-3-Clause
  *
  ******************************************************************************
  */
/* USER CODE END Header */
/* Includes ------------------------------------------------------------------*/
#include "main.h"

/* Private includes ----------------------------------------------------------*/
/* USER CODE BEGIN Includes */
#include "stm32_lpm.h"
#include "stm32_seq.h"
#include "dbg_trace.h"
#include "hw_conf.h"
#include "otp.h"
#include "string.h"
#include "app_conf.h"
/* USER CODE END Includes */

/* Private typedef -----------------------------------------------------------*/
/* USER CODE BEGIN PTD */

/* USER CODE END PTD */

/* Private define ------------------------------------------------------------*/
/* USER CODE BEGIN PD */
/* USER CODE END PD */

/* Private macro -------------------------------------------------------------*/
/* USER CODE BEGIN PM */

/* USER CODE END PM */

/* Private variables ---------------------------------------------------------*/
ADC_HandleTypeDef hadc1;
DMA_HandleTypeDef hdma_adc1;

IPCC_HandleTypeDef hipcc;

RTC_HandleTypeDef hrtc;

TIM_HandleTypeDef htim2;

UART_HandleTypeDef huart1;
DMA_HandleTypeDef hdma_usart1_tx;

/* USER CODE BEGIN PV */
uint8_t BTdata[72] = {0}; // This is declared in main.h
uint8_t RunningState = 0;
uint8_t TimeReady = 0;
uint8_t Custom_Notification = 0; //Custom
uint16_t ADC_Buffer[6] = {0};
uint8_t ADC_Read_Complete = 0;
/* USER CODE END PV */

/* Private function prototypes -----------------------------------------------*/
void SystemClock_Config(void);
static void MX_GPIO_Init(void);
static void MX_DMA_Init(void);
static void MX_IPCC_Init(void);
static void MX_RF_Init(void);
static void MX_RTC_Init(void);
static void MX_USART1_UART_Init(void);
static void MX_TIM2_Init(void);
static void MX_ADC1_Init(void);
/* USER CODE BEGIN PFP */
void PeriphClock_Config(void);
static void Reset_Device( void );
static void Reset_IPCC( void );
static void Reset_BackupDomain( void );
static void Init_Exti( void );
static void Config_HSE(void);
/* USER CODE END PFP */

/* Private user code ---------------------------------------------------------*/
/* USER CODE BEGIN 0 */

/* USER CODE END 0 */

/**
  * @brief  The application entry point.
  * @retval int
  */
int main(void)
{
  /* USER CODE BEGIN 1 */
  uint8_t i = 0;
  uint8_t UART_count = 0;
 // char UART_string[33] = {"\0"};
  char buffer[3];
  char char_buffer[4];
  char UART_String[98] = {0};
  char ADC_UART_String[33] = {0};
  UART_String[97] = 10; // line feed
  UART_String[96] = 13; // carriage return
  Custom_Notification = 0;
  uint8_t SequenceLoop = 0;
  uint8_t UART_Transmit_ADC_values = 0;
  uint8_t ADC_Read_Array_Complete = 0;
  uint16_t BatV = 0;
  GPIO_InitTypeDef GPIO_ChgMode = {0}; //This is used to change GPIO mode

  /**
   * The OPTVERR flag is wrongly set at power on
   * It shall be cleared before using any HAL_FLASH_xxx() api
   */
  __HAL_FLASH_CLEAR_FLAG(FLASH_FLAG_OPTVERR);

  /* USER CODE END 1 */

  /* MCU Configuration--------------------------------------------------------*/

  /* Reset of all peripherals, Initializes the Flash interface and the Systick. */
  HAL_Init();

  /* USER CODE BEGIN Init */
  Reset_Device();
  Config_HSE();
	
  /* USER CODE END Init */

  /* Configure the system clock */
  SystemClock_Config();

  /* IPCC initialisation */
   MX_IPCC_Init();

  /* USER CODE BEGIN SysInit */
  PeriphClock_Config();
  Init_Exti(); /**< Configure the system Power Mode */
  /* USER CODE END SysInit */

  /* Initialize all configured peripherals */
  MX_GPIO_Init();
  MX_DMA_Init();
  MX_RF_Init();
  MX_RTC_Init();
  MX_USART1_UART_Init();
  MX_TIM2_Init();
  MX_ADC1_Init();
  /* USER CODE BEGIN 2 */

  // Calibration for ADC
  HAL_ADCEx_Calibration_Start(&hadc1, ADC_SINGLE_ENDED);

  UART_Transmit_ADC_values = 0;
  /* USER CODE END 2 */

  /* Init code for STM32_WPAN */
  APPE_Init();
  /* Infinite loop */
  /* USER CODE BEGIN WHILE */
  
  HAL_TIM_Base_Start_IT(&htim2); //start timer2 with interrupt
  
  while (1)
  {
  	
    /* USER CODE END WHILE */

    /* USER CODE BEGIN 3 */
	UTIL_SEQ_Run( UTIL_SEQ_DEFAULT );

	// RunningState = 1 means BLE is running
	// This if function is meant to let STM micro to send data to computer once data is compiled.
	if ((RunningState == 1) && (ADC_Read_Array_Complete == 1)) {

/*
		// Update data variable
		for (i=0; i<sizeof(BTdata); i++) {
			// update variable
			BTdata[i] += 1;

			// if data is more than 31, reset to 0
			if (BTdata[i] > 31) {
				BTdata[i] = 0;
			}

//				// Making a char array for transmitting via UART for checking
//				itoa(BTdata[i], buffer, 10);
//
//				if(BTdata[i] <10){
//					UART_String[i*3] = 48; //48 is ascii for "0"
//					UART_String[i*3+1] = buffer[0];
//					UART_String[i*3+2] = 44; //44 is ascii for ","
//				}
//				else {
//					UART_String[i*3] = buffer[0];
//					UART_String[i*3+1] = buffer[1];
//					UART_String[i*3+2] = 44;
//				}

		}
*/
		// Compile data into an array for sending via BLE

		RunningState = 0; // reset variable
		UTIL_SEQ_SetTask(1<<CFG_TASK_SW1_BUTTON_PUSHED_ID, CFG_SCH_PRIO_0);
		// Temporarily disable the UART transmit to reduce time for processing
		// HAL_UART_Transmit(&huart1, &UART_String, sizeof(UART_String), 100); // Send data via UART (working)
	}

	if (TimeReady == 1) {

		// reset variables
		SequenceLoop = 0;
		TimeReady = 0; // reset trigger

		// start GPIO1

		// Set GPIO from to Output Push Pull mode
		GPIO_ChgMode.Pin = GPIO1_Pin;
		GPIO_ChgMode.Mode = GPIO_MODE_OUTPUT_PP;
		GPIO_ChgMode.Pull = GPIO_NOPULL;
		GPIO_ChgMode.Speed = GPIO_SPEED_FREQ_LOW;
		HAL_GPIO_Init(GPIO1_GPIO_Port, &GPIO_ChgMode);
		HAL_GPIO_WritePin(GPIO1_GPIO_Port, GPIO1_Pin, GPIO_PIN_SET);

//		HAL_GPIO_WritePin(GPIO1_GPIO_Port, GPIO1_Pin, GPIO_PIN_SET); // GPIO1
//		HAL_GPIO_WritePin(GPIO2_GPIO_Port, GPIO2_Pin, GPIO_PIN_RESET); // GPIO2
//		HAL_GPIO_WritePin(GPIO3_GPIO_Port, GPIO3_Pin, GPIO_PIN_RESET); // GPIO3
//		HAL_GPIO_WritePin(GPIO4_GPIO_Port, GPIO4_Pin, GPIO_PIN_RESET); // GPIO4
//		HAL_GPIO_WritePin(GPIO5_GPIO_Port, GPIO5_Pin, GPIO_PIN_RESET); // GPIO5
//		HAL_GPIO_WritePin(GPIO6_GPIO_Port, GPIO6_Pin, GPIO_PIN_RESET); // GPIO6

		// start adc conversion
		HAL_ADC_Start_DMA(&hadc1, &ADC_Buffer, 6); //This needs to be changed later, ADC reads 7 values

	}

	// ADC_Read_Complete only goes 1 when ADC conversion is finished
	if (ADC_Read_Complete == 1) {

		// Save data to BT array
		for (i=0; i<6; i++) {
			BTdata[SequenceLoop*12 + i*2] = ADC_Buffer[i]>>8; //high byte
			BTdata[SequenceLoop*12 + i*2 + 1] = ADC_Buffer[i]; //low byte
		}

		// UART Debug transmission, set UART_Transmit_ADC_values to 0 to quicken operation
		if (UART_Transmit_ADC_values == 1) {
			itoa(SequenceLoop, buffer, 10);
			buffer[1] = '=';
			buffer[2] = '>';
			HAL_UART_Transmit(&huart1, buffer, 3, 10); // Send data via UART (working)

			UART_count = 0;

			// Reading the ADC buffer results
			for (i=0; i<6; i++) {
				// Making a char array for transmitting via UART for checking
				itoa(ADC_Buffer[i], char_buffer, 10);

				if (ADC_Buffer[i] < 10) {
					ADC_UART_String[UART_count+0] = '0';
					ADC_UART_String[UART_count+1] = '0';
					ADC_UART_String[UART_count+2] = '0';
					ADC_UART_String[UART_count+3] = char_buffer[0];
					ADC_UART_String[UART_count+4] = 44; //44 is ascii for ","
					UART_count += 5;
				}
				else if (ADC_Buffer[i] < 100) {
					ADC_UART_String[UART_count+0] = '0';
					ADC_UART_String[UART_count+1] = '0';
					ADC_UART_String[UART_count+2] = char_buffer[0];
					ADC_UART_String[UART_count+3] = char_buffer[1];
					ADC_UART_String[UART_count+4] = 44; //44 is ascii for ","
					UART_count += 5;
				}
				else if (ADC_Buffer[i] < 1000) {
					ADC_UART_String[UART_count+0] = '0';
					ADC_UART_String[UART_count+1] = char_buffer[0];
					ADC_UART_String[UART_count+2] = char_buffer[1];
					ADC_UART_String[UART_count+3] = char_buffer[2];
					ADC_UART_String[UART_count+4] = 44; //44 is ascii for ","
				}

				else {
					ADC_UART_String[UART_count+0] = char_buffer[0];
					ADC_UART_String[UART_count+1] = char_buffer[1];
					ADC_UART_String[UART_count+2] = char_buffer[2];
					ADC_UART_String[UART_count+3] = char_buffer[3];
					ADC_UART_String[UART_count+4] = 44; //44 is ascii for ","
					UART_count += 5;
				}
			}

			ADC_UART_String[UART_count] = 'A';
			ADC_UART_String[UART_count+1] = '\n';
			ADC_UART_String[UART_count+2] = '\r';

			HAL_UART_Transmit(&huart1, &ADC_UART_String, UART_count+3, 50); // Send data via UART (working)
		}

		ADC_Read_Complete = 0;
		SequenceLoop++;

		// Set the appropriate GPIO pins
		if (SequenceLoop == 1) {
			// Reset GPIO output to 0V/GND
			HAL_GPIO_WritePin(GPIO1_GPIO_Port, GPIO1_Pin, GPIO_PIN_RESET);

			// Set GPIO back to Analog
			GPIO_ChgMode.Pin = GPIO1_Pin;
			GPIO_ChgMode.Mode = GPIO_MODE_ANALOG;
			GPIO_ChgMode.Pull = GPIO_NOPULL;
			HAL_GPIO_Init(GPIO1_GPIO_Port, &GPIO_ChgMode);

			// Set GPIO to Output Push Pull
			GPIO_ChgMode.Pin = GPIO2_Pin;
			GPIO_ChgMode.Mode = GPIO_MODE_OUTPUT_PP;
			GPIO_ChgMode.Pull = GPIO_NOPULL;
			GPIO_ChgMode.Speed = GPIO_SPEED_FREQ_LOW;
			HAL_GPIO_Init(GPIO2_GPIO_Port, &GPIO_ChgMode);
			HAL_GPIO_WritePin(GPIO2_GPIO_Port, GPIO2_Pin, GPIO_PIN_SET);

//			HAL_GPIO_WritePin(GPIO1_GPIO_Port, GPIO1_Pin, GPIO_PIN_RESET); // GPIO1
//			HAL_GPIO_WritePin(GPIO2_GPIO_Port, GPIO2_Pin, GPIO_PIN_SET);   // GPIO2
//			HAL_GPIO_WritePin(GPIO3_GPIO_Port, GPIO3_Pin, GPIO_PIN_RESET); // GPIO3
//			HAL_GPIO_WritePin(GPIO4_GPIO_Port, GPIO4_Pin, GPIO_PIN_RESET); // GPIO4
//			HAL_GPIO_WritePin(GPIO5_GPIO_Port, GPIO5_Pin, GPIO_PIN_RESET); // GPIO5
//			HAL_GPIO_WritePin(GPIO6_GPIO_Port, GPIO6_Pin, GPIO_PIN_RESET); // GPIO6
		}
		else if (SequenceLoop == 2) {

			// Reset GPIO output to 0V/GND
			HAL_GPIO_WritePin(GPIO2_GPIO_Port, GPIO2_Pin, GPIO_PIN_RESET);

			// Set GPIO back to Analog
			GPIO_ChgMode.Pin = GPIO2_Pin;
			GPIO_ChgMode.Mode = GPIO_MODE_ANALOG;
			GPIO_ChgMode.Pull = GPIO_NOPULL;
			HAL_GPIO_Init(GPIO2_GPIO_Port, &GPIO_ChgMode);

			// Set GPIO to Output Push Pull
			GPIO_ChgMode.Pin = GPIO3_Pin;
			GPIO_ChgMode.Mode = GPIO_MODE_OUTPUT_PP;
			GPIO_ChgMode.Pull = GPIO_NOPULL;
			GPIO_ChgMode.Speed = GPIO_SPEED_FREQ_LOW;
			HAL_GPIO_Init(GPIO3_GPIO_Port, &GPIO_ChgMode);
			HAL_GPIO_WritePin(GPIO3_GPIO_Port, GPIO3_Pin, GPIO_PIN_SET);

//			HAL_GPIO_WritePin(GPIO1_GPIO_Port, GPIO1_Pin, GPIO_PIN_RESET); // GPIO1
//			HAL_GPIO_WritePin(GPIO2_GPIO_Port, GPIO2_Pin, GPIO_PIN_RESET); // GPIO2
//			HAL_GPIO_WritePin(GPIO3_GPIO_Port, GPIO3_Pin, GPIO_PIN_SET);   // GPIO3
//			HAL_GPIO_WritePin(GPIO4_GPIO_Port, GPIO4_Pin, GPIO_PIN_RESET); // GPIO4
//			HAL_GPIO_WritePin(GPIO5_GPIO_Port, GPIO5_Pin, GPIO_PIN_RESET); // GPIO5
//			HAL_GPIO_WritePin(GPIO6_GPIO_Port, GPIO6_Pin, GPIO_PIN_RESET); // GPIO6
		}
		else if (SequenceLoop == 3) {
			// Reset GPIO output to 0V/GND
			HAL_GPIO_WritePin(GPIO3_GPIO_Port, GPIO3_Pin, GPIO_PIN_RESET);

			// Set GPIO back to Analog
			GPIO_ChgMode.Pin = GPIO3_Pin;
			GPIO_ChgMode.Mode = GPIO_MODE_ANALOG;
			GPIO_ChgMode.Pull = GPIO_NOPULL;
			HAL_GPIO_Init(GPIO3_GPIO_Port, &GPIO_ChgMode);

			// Set GPIO to Output Push Pull
			GPIO_ChgMode.Pin = GPIO4_Pin;
			GPIO_ChgMode.Mode = GPIO_MODE_OUTPUT_PP;
			GPIO_ChgMode.Pull = GPIO_NOPULL;
			GPIO_ChgMode.Speed = GPIO_SPEED_FREQ_LOW;
			HAL_GPIO_Init(GPIO4_GPIO_Port, &GPIO_ChgMode);
			HAL_GPIO_WritePin(GPIO4_GPIO_Port, GPIO4_Pin, GPIO_PIN_SET);

//			HAL_GPIO_WritePin(GPIO1_GPIO_Port, GPIO1_Pin, GPIO_PIN_RESET); // GPIO1
//			HAL_GPIO_WritePin(GPIO2_GPIO_Port, GPIO2_Pin, GPIO_PIN_RESET); // GPIO2
//			HAL_GPIO_WritePin(GPIO3_GPIO_Port, GPIO3_Pin, GPIO_PIN_RESET); // GPIO3
//			HAL_GPIO_WritePin(GPIO4_GPIO_Port, GPIO4_Pin, GPIO_PIN_SET); // GPIO4
//			HAL_GPIO_WritePin(GPIO5_GPIO_Port, GPIO5_Pin, GPIO_PIN_RESET); // GPIO5
//			HAL_GPIO_WritePin(GPIO6_GPIO_Port, GPIO6_Pin, GPIO_PIN_RESET); // GPIO6
		}
		else if (SequenceLoop == 4) {
			// Reset GPIO output to 0V/GND
			HAL_GPIO_WritePin(GPIO4_GPIO_Port, GPIO4_Pin, GPIO_PIN_RESET);

			// Set GPIO back to Analog
			GPIO_ChgMode.Pin = GPIO4_Pin;
			GPIO_ChgMode.Mode = GPIO_MODE_ANALOG;
			GPIO_ChgMode.Pull = GPIO_NOPULL;
			HAL_GPIO_Init(GPIO4_GPIO_Port, &GPIO_ChgMode);

			// Set GPIO to Output Push Pull
			GPIO_ChgMode.Pin = GPIO5_Pin;
			GPIO_ChgMode.Mode = GPIO_MODE_OUTPUT_PP;
			GPIO_ChgMode.Pull = GPIO_NOPULL;
			GPIO_ChgMode.Speed = GPIO_SPEED_FREQ_LOW;
			HAL_GPIO_Init(GPIO5_GPIO_Port, &GPIO_ChgMode);
			HAL_GPIO_WritePin(GPIO5_GPIO_Port, GPIO5_Pin, GPIO_PIN_SET);

//			HAL_GPIO_WritePin(GPIO1_GPIO_Port, GPIO1_Pin, GPIO_PIN_RESET); // GPIO1
//			HAL_GPIO_WritePin(GPIO2_GPIO_Port, GPIO2_Pin, GPIO_PIN_RESET); // GPIO2
//			HAL_GPIO_WritePin(GPIO3_GPIO_Port, GPIO3_Pin, GPIO_PIN_RESET); // GPIO3
//			HAL_GPIO_WritePin(GPIO4_GPIO_Port, GPIO4_Pin, GPIO_PIN_RESET); // GPIO4
//			HAL_GPIO_WritePin(GPIO5_GPIO_Port, GPIO5_Pin, GPIO_PIN_SET); // GPIO5
//			HAL_GPIO_WritePin(GPIO6_GPIO_Port, GPIO6_Pin, GPIO_PIN_RESET); // GPIO6
		}
		else if (SequenceLoop == 5) {
			// Reset GPIO output to 0V/GND
			HAL_GPIO_WritePin(GPIO5_GPIO_Port, GPIO5_Pin, GPIO_PIN_RESET);

			// Set GPIO back to Analog
			GPIO_ChgMode.Pin = GPIO5_Pin;
			GPIO_ChgMode.Mode = GPIO_MODE_ANALOG;
			GPIO_ChgMode.Pull = GPIO_NOPULL;
			HAL_GPIO_Init(GPIO5_GPIO_Port, &GPIO_ChgMode);

			// Set GPIO to Output Push Pull
			GPIO_ChgMode.Pin = GPIO6_Pin;
			GPIO_ChgMode.Mode = GPIO_MODE_OUTPUT_PP;
			GPIO_ChgMode.Pull = GPIO_NOPULL;
			GPIO_ChgMode.Speed = GPIO_SPEED_FREQ_LOW;
			HAL_GPIO_Init(GPIO6_GPIO_Port, &GPIO_ChgMode);
			HAL_GPIO_WritePin(GPIO6_GPIO_Port, GPIO6_Pin, GPIO_PIN_SET);

//			HAL_GPIO_WritePin(GPIO1_GPIO_Port, GPIO1_Pin, GPIO_PIN_RESET); // GPIO1
//			HAL_GPIO_WritePin(GPIO2_GPIO_Port, GPIO2_Pin, GPIO_PIN_RESET); // GPIO2
//			HAL_GPIO_WritePin(GPIO3_GPIO_Port, GPIO3_Pin, GPIO_PIN_RESET); // GPIO3
//			HAL_GPIO_WritePin(GPIO4_GPIO_Port, GPIO4_Pin, GPIO_PIN_RESET); // GPIO4
//			HAL_GPIO_WritePin(GPIO5_GPIO_Port, GPIO5_Pin, GPIO_PIN_RESET); // GPIO5
//			HAL_GPIO_WritePin(GPIO6_GPIO_Port, GPIO6_Pin, GPIO_PIN_SET); // GPIO6
		}

		// once all ADC reading is done
		if (SequenceLoop >= 6) {

			if (UART_Transmit_ADC_values == 1) {
				HAL_UART_Transmit(&huart1, '\n\r', 2, 20); // Send data via UART
			}

			// reset all GPIO
			// Reset GPIO output to 0V/GND
			HAL_GPIO_WritePin(GPIO6_GPIO_Port, GPIO6_Pin, GPIO_PIN_RESET);

			// Set GPIO back to Analog
			GPIO_ChgMode.Pin = GPIO6_Pin;
			GPIO_ChgMode.Mode = GPIO_MODE_ANALOG;
			GPIO_ChgMode.Pull = GPIO_NOPULL;
			HAL_GPIO_Init(GPIO6_GPIO_Port, &GPIO_ChgMode);


//			HAL_GPIO_WritePin(GPIO1_GPIO_Port, GPIO1_Pin, GPIO_PIN_RESET); // GPIO1
//			HAL_GPIO_WritePin(GPIO2_GPIO_Port, GPIO2_Pin, GPIO_PIN_RESET); // GPIO2
//			HAL_GPIO_WritePin(GPIO3_GPIO_Port, GPIO3_Pin, GPIO_PIN_RESET); // GPIO3
//			HAL_GPIO_WritePin(GPIO4_GPIO_Port, GPIO4_Pin, GPIO_PIN_RESET); // GPIO4
//			HAL_GPIO_WritePin(GPIO5_GPIO_Port, GPIO5_Pin, GPIO_PIN_RESET); // GPIO5
//			HAL_GPIO_WritePin(GPIO6_GPIO_Port, GPIO6_Pin, GPIO_PIN_RESET); // GPIO6

			ADC_Read_Array_Complete = 1;
		}
		else {
			HAL_ADC_Start_DMA(&hadc1, &ADC_Buffer, 6); // Start conversion
		}

	}
  }
  /* USER CODE END 3 */
}

/**
  * @brief System Clock Configuration
  * @retval None
  */
void SystemClock_Config(void)
{
  RCC_OscInitTypeDef RCC_OscInitStruct = {0};
  RCC_ClkInitTypeDef RCC_ClkInitStruct = {0};
  RCC_PeriphCLKInitTypeDef PeriphClkInitStruct = {0};

  /** Configure LSE Drive Capability
  */
  HAL_PWR_EnableBkUpAccess();
  __HAL_RCC_LSEDRIVE_CONFIG(RCC_LSEDRIVE_LOW);
  /** Initializes the RCC Oscillators according to the specified parameters
  * in the RCC_OscInitTypeDef structure.
  */
  RCC_OscInitStruct.OscillatorType = RCC_OSCILLATORTYPE_HSI|RCC_OSCILLATORTYPE_HSE
                              |RCC_OSCILLATORTYPE_LSE;
  RCC_OscInitStruct.HSEState = RCC_HSE_ON;
  RCC_OscInitStruct.LSEState = RCC_LSE_ON;
  RCC_OscInitStruct.HSIState = RCC_HSI_ON;
  RCC_OscInitStruct.HSICalibrationValue = RCC_HSICALIBRATION_DEFAULT;
  RCC_OscInitStruct.PLL.PLLState = RCC_PLL_NONE;
  if (HAL_RCC_OscConfig(&RCC_OscInitStruct) != HAL_OK)
  {
    Error_Handler();
  }
  /** Configure the SYSCLKSource, HCLK, PCLK1 and PCLK2 clocks dividers
  */
  RCC_ClkInitStruct.ClockType = RCC_CLOCKTYPE_HCLK4|RCC_CLOCKTYPE_HCLK2
                              |RCC_CLOCKTYPE_HCLK|RCC_CLOCKTYPE_SYSCLK
                              |RCC_CLOCKTYPE_PCLK1|RCC_CLOCKTYPE_PCLK2;
  RCC_ClkInitStruct.SYSCLKSource = RCC_SYSCLKSOURCE_HSE;
  RCC_ClkInitStruct.AHBCLKDivider = RCC_SYSCLK_DIV1;
  RCC_ClkInitStruct.APB1CLKDivider = RCC_HCLK_DIV1;
  RCC_ClkInitStruct.APB2CLKDivider = RCC_HCLK_DIV1;
  RCC_ClkInitStruct.AHBCLK2Divider = RCC_SYSCLK_DIV1;
  RCC_ClkInitStruct.AHBCLK4Divider = RCC_SYSCLK_DIV1;

  if (HAL_RCC_ClockConfig(&RCC_ClkInitStruct, FLASH_LATENCY_1) != HAL_OK)
  {
    Error_Handler();
  }
  /** Initializes the peripherals clocks
  */
  PeriphClkInitStruct.PeriphClockSelection = RCC_PERIPHCLK_RFWAKEUP|RCC_PERIPHCLK_RTC
                              |RCC_PERIPHCLK_USART1|RCC_PERIPHCLK_ADC;
  PeriphClkInitStruct.Usart1ClockSelection = RCC_USART1CLKSOURCE_PCLK2;
  PeriphClkInitStruct.AdcClockSelection = RCC_ADCCLKSOURCE_SYSCLK;
  PeriphClkInitStruct.RTCClockSelection = RCC_RTCCLKSOURCE_LSE;
  PeriphClkInitStruct.RFWakeUpClockSelection = RCC_RFWKPCLKSOURCE_LSE;
  if (HAL_RCCEx_PeriphCLKConfig(&PeriphClkInitStruct) != HAL_OK)
  {
    Error_Handler();
  }
}

/**
  * @brief ADC1 Initialization Function
  * @param None
  * @retval None
  */
static void MX_ADC1_Init(void)
{

  /* USER CODE BEGIN ADC1_Init 0 */

  /* USER CODE END ADC1_Init 0 */

  ADC_ChannelConfTypeDef sConfig = {0};

  /* USER CODE BEGIN ADC1_Init 1 */

  /* USER CODE END ADC1_Init 1 */
  /** Common config
  */
  hadc1.Instance = ADC1;
  hadc1.Init.ClockPrescaler = ADC_CLOCK_ASYNC_DIV1;
  hadc1.Init.Resolution = ADC_RESOLUTION_12B;
  hadc1.Init.DataAlign = ADC_DATAALIGN_RIGHT;
  hadc1.Init.ScanConvMode = ADC_SCAN_ENABLE;
  hadc1.Init.EOCSelection = ADC_EOC_SINGLE_CONV;
  hadc1.Init.LowPowerAutoWait = DISABLE;
  hadc1.Init.ContinuousConvMode = DISABLE;
  hadc1.Init.NbrOfConversion = 6;
  hadc1.Init.DiscontinuousConvMode = DISABLE;
  hadc1.Init.ExternalTrigConv = ADC_SOFTWARE_START;
  hadc1.Init.ExternalTrigConvEdge = ADC_EXTERNALTRIGCONVEDGE_NONE;
  hadc1.Init.DMAContinuousRequests = ENABLE;
  hadc1.Init.Overrun = ADC_OVR_DATA_PRESERVED;
  hadc1.Init.OversamplingMode = DISABLE;
  if (HAL_ADC_Init(&hadc1) != HAL_OK)
  {
    Error_Handler();
  }
  /** Configure Regular Channel
  */
  sConfig.Channel = ADC_CHANNEL_5;
  sConfig.Rank = ADC_REGULAR_RANK_1;
  sConfig.SamplingTime = ADC_SAMPLETIME_24CYCLES_5;
  sConfig.SingleDiff = ADC_SINGLE_ENDED;
  sConfig.OffsetNumber = ADC_OFFSET_NONE;
  sConfig.Offset = 0;
  if (HAL_ADC_ConfigChannel(&hadc1, &sConfig) != HAL_OK)
  {
    Error_Handler();
  }
  /** Configure Regular Channel
  */
  sConfig.Channel = ADC_CHANNEL_6;
  sConfig.Rank = ADC_REGULAR_RANK_2;
  if (HAL_ADC_ConfigChannel(&hadc1, &sConfig) != HAL_OK)
  {
    Error_Handler();
  }
  /** Configure Regular Channel
  */
  sConfig.Channel = ADC_CHANNEL_7;
  sConfig.Rank = ADC_REGULAR_RANK_3;
  if (HAL_ADC_ConfigChannel(&hadc1, &sConfig) != HAL_OK)
  {
    Error_Handler();
  }
  /** Configure Regular Channel
  */
  sConfig.Channel = ADC_CHANNEL_8;
  sConfig.Rank = ADC_REGULAR_RANK_4;
  if (HAL_ADC_ConfigChannel(&hadc1, &sConfig) != HAL_OK)
  {
    Error_Handler();
  }
  /** Configure Regular Channel
  */
  sConfig.Channel = ADC_CHANNEL_9;
  sConfig.Rank = ADC_REGULAR_RANK_5;
  if (HAL_ADC_ConfigChannel(&hadc1, &sConfig) != HAL_OK)
  {
    Error_Handler();
  }
  /** Configure Regular Channel
  */
  sConfig.Channel = ADC_CHANNEL_10;
  sConfig.Rank = ADC_REGULAR_RANK_6;
  if (HAL_ADC_ConfigChannel(&hadc1, &sConfig) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN ADC1_Init 2 */

  /* USER CODE END ADC1_Init 2 */

}

/**
  * @brief IPCC Initialization Function
  * @param None
  * @retval None
  */
static void MX_IPCC_Init(void)
{

  /* USER CODE BEGIN IPCC_Init 0 */

  /* USER CODE END IPCC_Init 0 */

  /* USER CODE BEGIN IPCC_Init 1 */

  /* USER CODE END IPCC_Init 1 */
  hipcc.Instance = IPCC;
  if (HAL_IPCC_Init(&hipcc) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN IPCC_Init 2 */

  /* USER CODE END IPCC_Init 2 */

}

/**
  * @brief RF Initialization Function
  * @param None
  * @retval None
  */
static void MX_RF_Init(void)
{

  /* USER CODE BEGIN RF_Init 0 */

  /* USER CODE END RF_Init 0 */

  /* USER CODE BEGIN RF_Init 1 */

  /* USER CODE END RF_Init 1 */
  /* USER CODE BEGIN RF_Init 2 */

  /* USER CODE END RF_Init 2 */

}

/**
  * @brief RTC Initialization Function
  * @param None
  * @retval None
  */
static void MX_RTC_Init(void)
{

  /* USER CODE BEGIN RTC_Init 0 */

  /* USER CODE END RTC_Init 0 */

  /* USER CODE BEGIN RTC_Init 1 */

  /* USER CODE END RTC_Init 1 */
  /** Initialize RTC Only
  */
  hrtc.Instance = RTC;
  hrtc.Init.HourFormat = RTC_HOURFORMAT_24;
  hrtc.Init.AsynchPrediv = CFG_RTC_ASYNCH_PRESCALER;
  hrtc.Init.SynchPrediv = CFG_RTC_SYNCH_PRESCALER;
  hrtc.Init.OutPut = RTC_OUTPUT_DISABLE;
  hrtc.Init.OutPutPolarity = RTC_OUTPUT_POLARITY_HIGH;
  hrtc.Init.OutPutType = RTC_OUTPUT_TYPE_OPENDRAIN;
  hrtc.Init.OutPutRemap = RTC_OUTPUT_REMAP_NONE;
  if (HAL_RTC_Init(&hrtc) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN RTC_Init 2 */

  /* USER CODE END RTC_Init 2 */

}

/**
  * @brief TIM2 Initialization Function
  * @param None
  * @retval None
  */
static void MX_TIM2_Init(void)
{

  /* USER CODE BEGIN TIM2_Init 0 */

  /* USER CODE END TIM2_Init 0 */

  TIM_ClockConfigTypeDef sClockSourceConfig = {0};
  TIM_MasterConfigTypeDef sMasterConfig = {0};

  /* USER CODE BEGIN TIM2_Init 1 */

  /* USER CODE END TIM2_Init 1 */
  htim2.Instance = TIM2;
  htim2.Init.Prescaler = 3199;
  htim2.Init.CounterMode = TIM_COUNTERMODE_UP;
  htim2.Init.Period = 999;
  htim2.Init.ClockDivision = TIM_CLOCKDIVISION_DIV1;
  htim2.Init.AutoReloadPreload = TIM_AUTORELOAD_PRELOAD_ENABLE;
  if (HAL_TIM_Base_Init(&htim2) != HAL_OK)
  {
    Error_Handler();
  }
  sClockSourceConfig.ClockSource = TIM_CLOCKSOURCE_INTERNAL;
  if (HAL_TIM_ConfigClockSource(&htim2, &sClockSourceConfig) != HAL_OK)
  {
    Error_Handler();
  }
  sMasterConfig.MasterOutputTrigger = TIM_TRGO_RESET;
  sMasterConfig.MasterSlaveMode = TIM_MASTERSLAVEMODE_DISABLE;
  if (HAL_TIMEx_MasterConfigSynchronization(&htim2, &sMasterConfig) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN TIM2_Init 2 */

  /* USER CODE END TIM2_Init 2 */

}

/**
  * @brief USART1 Initialization Function
  * @param None
  * @retval None
  */
static void MX_USART1_UART_Init(void)
{

  /* USER CODE BEGIN USART1_Init 0 */

  /* USER CODE END USART1_Init 0 */

  /* USER CODE BEGIN USART1_Init 1 */

  /* USER CODE END USART1_Init 1 */
  huart1.Instance = USART1;
  huart1.Init.BaudRate = 115200;
  huart1.Init.WordLength = UART_WORDLENGTH_8B;
  huart1.Init.StopBits = UART_STOPBITS_1;
  huart1.Init.Parity = UART_PARITY_NONE;
  huart1.Init.Mode = UART_MODE_TX_RX;
  huart1.Init.HwFlowCtl = UART_HWCONTROL_NONE;
  huart1.Init.OverSampling = UART_OVERSAMPLING_16;
  huart1.Init.OneBitSampling = UART_ONE_BIT_SAMPLE_DISABLE;
  huart1.Init.ClockPrescaler = UART_PRESCALER_DIV1;
  huart1.AdvancedInit.AdvFeatureInit = UART_ADVFEATURE_NO_INIT;
  if (HAL_UART_Init(&huart1) != HAL_OK)
  {
    Error_Handler();
  }
  if (HAL_UARTEx_SetTxFifoThreshold(&huart1, UART_TXFIFO_THRESHOLD_1_8) != HAL_OK)
  {
    Error_Handler();
  }
  if (HAL_UARTEx_SetRxFifoThreshold(&huart1, UART_RXFIFO_THRESHOLD_1_8) != HAL_OK)
  {
    Error_Handler();
  }
  if (HAL_UARTEx_DisableFifoMode(&huart1) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN USART1_Init 2 */

  /* USER CODE END USART1_Init 2 */

}

/**
  * Enable DMA controller clock
  */
static void MX_DMA_Init(void)
{

  /* DMA controller clock enable */
  __HAL_RCC_DMAMUX1_CLK_ENABLE();
  __HAL_RCC_DMA1_CLK_ENABLE();

  /* DMA interrupt init */
  /* DMA1_Channel1_IRQn interrupt configuration */
  HAL_NVIC_SetPriority(DMA1_Channel1_IRQn, 0, 0);
  HAL_NVIC_EnableIRQ(DMA1_Channel1_IRQn);
  /* DMA1_Channel2_IRQn interrupt configuration */
  HAL_NVIC_SetPriority(DMA1_Channel2_IRQn, 0, 0);
  HAL_NVIC_EnableIRQ(DMA1_Channel2_IRQn);

}

/**
  * @brief GPIO Initialization Function
  * @param None
  * @retval None
  */
static void MX_GPIO_Init(void)
{
  GPIO_InitTypeDef GPIO_InitStruct = {0};

  /* GPIO Ports Clock Enable */
  __HAL_RCC_GPIOC_CLK_ENABLE();
  __HAL_RCC_GPIOB_CLK_ENABLE();
  __HAL_RCC_GPIOA_CLK_ENABLE();

  /*Configure GPIO pin Output Level */
  HAL_GPIO_WritePin(GPIOB, LED1_Pin|LED2_Pin, GPIO_PIN_RESET);

  /*Configure GPIO pins : GPIO6_Pin GPIO5_Pin GPIO1_Pin */
  GPIO_InitStruct.Pin = GPIO6_Pin|GPIO5_Pin|GPIO1_Pin;
  GPIO_InitStruct.Mode = GPIO_MODE_ANALOG;
  GPIO_InitStruct.Pull = GPIO_NOPULL;
  HAL_GPIO_Init(GPIOB, &GPIO_InitStruct);

  /*Configure GPIO pins : PA6 GPIO4_Pin GPIO3_Pin GPIO2_Pin */
  GPIO_InitStruct.Pin = GPIO_PIN_6|GPIO4_Pin|GPIO3_Pin|GPIO2_Pin;
  GPIO_InitStruct.Mode = GPIO_MODE_ANALOG;
  GPIO_InitStruct.Pull = GPIO_NOPULL;
  HAL_GPIO_Init(GPIOA, &GPIO_InitStruct);

  /*Configure GPIO pins : LED1_Pin LED2_Pin */
  GPIO_InitStruct.Pin = LED1_Pin|LED2_Pin;
  GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
  GPIO_InitStruct.Pull = GPIO_NOPULL;
  GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
  HAL_GPIO_Init(GPIOB, &GPIO_InitStruct);

}

/* USER CODE BEGIN 4 */

void PeriphClock_Config(void)
{
  #if (CFG_USB_INTERFACE_ENABLE != 0)
	RCC_PeriphCLKInitTypeDef PeriphClkInitStruct = { 0 };
	RCC_CRSInitTypeDef RCC_CRSInitStruct = { 0 };

	/**
   * This prevents the CPU2 to disable the HSI48 oscillator when
   * it does not use anymore the RNG IP
   */
  LL_HSEM_1StepLock( HSEM, 5 );

  LL_RCC_HSI48_Enable();

	while(!LL_RCC_HSI48_IsReady());

	/* Select HSI48 as USB clock source */
	PeriphClkInitStruct.PeriphClockSelection = RCC_PERIPHCLK_USB;
	PeriphClkInitStruct.UsbClockSelection = RCC_USBCLKSOURCE_HSI48;
	HAL_RCCEx_PeriphCLKConfig(&PeriphClkInitStruct);

	/*Configure the clock recovery system (CRS)**********************************/

	/* Enable CRS Clock */
	__HAL_RCC_CRS_CLK_ENABLE();

	/* Default Synchro Signal division factor (not divided) */
	RCC_CRSInitStruct.Prescaler = RCC_CRS_SYNC_DIV1;

	/* Set the SYNCSRC[1:0] bits according to CRS_Source value */
	RCC_CRSInitStruct.Source = RCC_CRS_SYNC_SOURCE_USB;

	/* HSI48 is synchronized with USB SOF at 1KHz rate */
	RCC_CRSInitStruct.ReloadValue = RCC_CRS_RELOADVALUE_DEFAULT;
	RCC_CRSInitStruct.ErrorLimitValue = RCC_CRS_ERRORLIMIT_DEFAULT;

	RCC_CRSInitStruct.Polarity = RCC_CRS_SYNC_POLARITY_RISING;

	/* Set the TRIM[5:0] to the default value*/
	RCC_CRSInitStruct.HSI48CalibrationValue = RCC_CRS_HSI48CALIBRATION_DEFAULT;

	/* Start automatic synchronization */
	HAL_RCCEx_CRSConfig(&RCC_CRSInitStruct);
#endif

	return;
}
/*************************************************************
 *
 * LOCAL FUNCTIONS
 *
 *************************************************************/

static void Config_HSE(void)
{
    OTP_ID0_t * p_otp;

  /**
   * Read HSE_Tuning from OTP
   */
  p_otp = (OTP_ID0_t *) OTP_Read(0);
  if (p_otp)
  {
    LL_RCC_HSE_SetCapacitorTuning(p_otp->hse_tuning);
  }

  return;
}  


static void Reset_Device( void )
{
#if ( CFG_HW_RESET_BY_FW == 1 )
	Reset_BackupDomain();

	Reset_IPCC();
#endif

	return;
}

static void Reset_IPCC( void )
{
	LL_AHB3_GRP1_EnableClock(LL_AHB3_GRP1_PERIPH_IPCC);

	LL_C1_IPCC_ClearFlag_CHx(
			IPCC,
			LL_IPCC_CHANNEL_1 | LL_IPCC_CHANNEL_2 | LL_IPCC_CHANNEL_3 | LL_IPCC_CHANNEL_4
			| LL_IPCC_CHANNEL_5 | LL_IPCC_CHANNEL_6);

	LL_C2_IPCC_ClearFlag_CHx(
			IPCC,
			LL_IPCC_CHANNEL_1 | LL_IPCC_CHANNEL_2 | LL_IPCC_CHANNEL_3 | LL_IPCC_CHANNEL_4
			| LL_IPCC_CHANNEL_5 | LL_IPCC_CHANNEL_6);

	LL_C1_IPCC_DisableTransmitChannel(
			IPCC,
			LL_IPCC_CHANNEL_1 | LL_IPCC_CHANNEL_2 | LL_IPCC_CHANNEL_3 | LL_IPCC_CHANNEL_4
			| LL_IPCC_CHANNEL_5 | LL_IPCC_CHANNEL_6);

	LL_C2_IPCC_DisableTransmitChannel(
			IPCC,
			LL_IPCC_CHANNEL_1 | LL_IPCC_CHANNEL_2 | LL_IPCC_CHANNEL_3 | LL_IPCC_CHANNEL_4
			| LL_IPCC_CHANNEL_5 | LL_IPCC_CHANNEL_6);

	LL_C1_IPCC_DisableReceiveChannel(
			IPCC,
			LL_IPCC_CHANNEL_1 | LL_IPCC_CHANNEL_2 | LL_IPCC_CHANNEL_3 | LL_IPCC_CHANNEL_4
			| LL_IPCC_CHANNEL_5 | LL_IPCC_CHANNEL_6);

	LL_C2_IPCC_DisableReceiveChannel(
			IPCC,
			LL_IPCC_CHANNEL_1 | LL_IPCC_CHANNEL_2 | LL_IPCC_CHANNEL_3 | LL_IPCC_CHANNEL_4
			| LL_IPCC_CHANNEL_5 | LL_IPCC_CHANNEL_6);

	return;
}

static void Reset_BackupDomain( void )
{
	if ((LL_RCC_IsActiveFlag_PINRST() != FALSE) && (LL_RCC_IsActiveFlag_SFTRST() == FALSE))
	{
		HAL_PWR_EnableBkUpAccess(); /**< Enable access to the RTC registers */

		/**
		 *  Write twice the value to flush the APB-AHB bridge
		 *  This bit shall be written in the register before writing the next one
		 */
		HAL_PWR_EnableBkUpAccess();

		__HAL_RCC_BACKUPRESET_FORCE();
		__HAL_RCC_BACKUPRESET_RELEASE();
	}

	return;
}

static void Init_Exti( void )
{
  /**< Disable all wakeup interrupt on CPU1  except IPCC(36), HSEM(38) */
  LL_EXTI_DisableIT_0_31(~0);
  LL_EXTI_DisableIT_32_63( (~0) & (~(LL_EXTI_LINE_36 | LL_EXTI_LINE_38)) );

  return;
}


void HAL_TIM_PeriodElapsedCallback(TIM_HandleTypeDef *htim) {
//	HAL_GPIO_TogglePin(LED2_GPIO_Port, LED2_Pin);

	if (Custom_Notification == 1) {
		// UTIL_SEQ_SetTask(1<<CFG_TASK_SW1_BUTTON_PUSHED_ID, CFG_SCH_PRIO_0);
		RunningState = 1;

		TimeReady = 1;
	}
	else {
		// Reset
		RunningState = 0;
		TimeReady = 0;
	}


}

// Interrupt when ADC completed conversion
void HAL_ADC_ConvCpltCallback(ADC_HandleTypeDef *hadc) {
	ADC_Read_Complete = 1;
}



/* USER CODE END 4 */

/**
  * @brief  This function is executed in case of error occurrence.
  * @retval None
  */
void Error_Handler(void)
{
  /* USER CODE BEGIN Error_Handler_Debug */
  /* User can add his own implementation to report the HAL error return state */
  __disable_irq();
  while (1)
  {
  }
  /* USER CODE END Error_Handler_Debug */
}

#ifdef  USE_FULL_ASSERT
/**
  * @brief  Reports the name of the source file and the source line number
  *         where the assert_param error has occurred.
  * @param  file: pointer to the source file name
  * @param  line: assert_param error line source number
  * @retval None
  */
void assert_failed(uint8_t *file, uint32_t line)
{
  /* USER CODE BEGIN 6 */
  /* User can add his own implementation to report the file name and line number,
     ex: printf("Wrong parameters value: file %s on line %d\r\n", file, line) */
  /* USER CODE END 6 */
}
#endif /* USE_FULL_ASSERT */

/************************ (C) COPYRIGHT STMicroelectronics *****END OF FILE****/
