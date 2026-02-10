/*
 * Copyright (c) 2017 Linaro Limited
 *
 * SPDX-License-Identifier: Apache-2.0
 */

#include <zephyr/kernel.h>
#include <zephyr/device.h>
#include <zephyr/drivers/gpio.h>
#include <zephyr/sys/printk.h>
#include <zephyr/sys/__assert.h>
#include <string.h>

#define STACKSIZE 1024

#define PRIORITY 7

/* 从设备树的 /aliases 节点获取名为 led0/led1 的节点标识符 (Node Identifier) */
#define LED0_NODE DT_ALIAS(led0)
#define LED1_NODE DT_ALIAS(led1)

/* 
 * 编译时检查：确保设备树中定义了该别名，并且其状态为 "okay"。
 * 如果开发板没有定义 led0 别名，编译器将报错。
 */
#if !DT_NODE_HAS_STATUS_OKAY(LED0_NODE)
#error "Unsupported board: led0 devicetree alias is not defined"
#endif

#if !DT_NODE_HAS_STATUS_OKAY(LED1_NODE)
#error "Unsupported board: led1 devicetree alias is not defined"
#endif

// FIFO 数据项结构体，第一个字段保留给内核链表指针使用
struct printk_data_t {
	void *fifo_reserved; /* 1st word reserved for use by fifo */
	uint32_t led;
	uint32_t cnt;
};

/**
 * @brief 静态定义并初始化一个 FIFO (First In, First Out) 队列
 * struct k_fifo printk_fifo ,with specified resource and gcc __attributes.
 */
K_FIFO_DEFINE(printk_fifo);

struct led {
	struct gpio_dt_spec spec;
	uint8_t num;
};

/* 
 * 初始化 LED 的硬件规格信息。
 * GPIO_DT_SPEC_GET_OR 从设备树节点提取：
 * 1. GPIO 控制器设备指针 (port)
 * 2. 引脚编号 (pin)
 * 3. 硬件标志位 (flags, 如 ACTIVE_LOW/HIGH)
 * 如果提取失败，则使用默认值 {0}。
 */
static const struct led led0 = {
	.spec = GPIO_DT_SPEC_GET_OR(LED0_NODE, gpios, {0}),
	.num = 0,
};

/**
 @brief 
 在 GPIO_DT_SPEC_GET_OR(node_id, prop, default_value) 中：
 1. GET:
    尝试从设备树（Devicetree）中读取指定的属性信息（如引脚号、控制器等）。
 2. OR: 如果设备树中没有定义这个属性，或者该节点不存在。
 3. Default: 则使用你提供的第三个参数（default_value）作为结果。

 4. API with no OR : 直接报错，而非返回default
 */
static const struct led led1 = {
	.spec = GPIO_DT_SPEC_GET_OR(LED1_NODE, gpios, {0}),
	.num = 1,
};

void blink(const struct led *led, uint32_t sleep_ms, uint32_t id)
{
	const struct gpio_dt_spec *spec = &led->spec;
	int cnt = 0;
	int ret;

	if (!device_is_ready(spec->port)) {
		printk("Error: %s device is not ready\n", spec->port->name);
		return;
	}

	ret = gpio_pin_configure_dt(spec, GPIO_OUTPUT);
	if (ret != 0) {
		printk("Error %d: failed to configure pin %d (LED '%d')\n",
			ret, spec->pin, led->num);
		return;
	}

	while (1) {
		gpio_pin_set(spec->port, spec->pin, cnt % 2);

		struct printk_data_t tx_data = { .led = id, .cnt = cnt };

		size_t size = sizeof(struct printk_data_t);
		char *mem_ptr = k_malloc(size);
		__ASSERT_NO_MSG(mem_ptr != 0);

		memcpy(mem_ptr, &tx_data, size);

		k_fifo_put(&printk_fifo, mem_ptr);

		k_msleep(sleep_ms);
		cnt++;
	}
}

void blink0(void)
{
	blink(&led0, 100, 0);
}

void blink1(void)
{
	blink(&led1, 1000, 1);
}

void uart_out(void)
{
	while (1) {
		//* 阻塞方法，无数据时挂起线程
		struct printk_data_t *rx_data = k_fifo_get(&printk_fifo,
							   K_FOREVER);
		printk("Toggled led%d; counter=%d\n",
		       rx_data->led, rx_data->cnt);
		k_free(rx_data);
	}
}

K_THREAD_DEFINE(blink0_id, STACKSIZE, blink0, NULL, NULL, NULL,
		PRIORITY, 0, 0);
K_THREAD_DEFINE(blink1_id, STACKSIZE, blink1, NULL, NULL, NULL,
		PRIORITY, 0, 0);
K_THREAD_DEFINE(uart_out_id, STACKSIZE, uart_out, NULL, NULL, NULL,
		PRIORITY, 0, 0);
