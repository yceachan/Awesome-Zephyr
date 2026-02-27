/*
 * Copyright (c) 2022 Rodrigo Peixoto <rodrigopex@gmail.com>
 * SPDX-License-Identifier: Apache-2.0
 */

#include <stdint.h>

#include <zephyr/kernel.h>
#include <zephyr/logging/log.h>
#include <zephyr/zbus/zbus.h>
LOG_MODULE_DECLARE(zbus, CONFIG_ZBUS_LOG_LEVEL);

/**
 * @brief 版本信息消息结构体
 */
struct version_msg {
	uint8_t major;
	uint8_t minor;
	uint16_t build;
};

/**
 * @brief 模拟加速度计消息结构体
 */
struct acc_msg {
	int x;
	int y;
	int z;
};

/**
 * @brief 定义版本通道 (version_chan)
 * 
 * 这是一个静态配置的通道，没有观察者，仅提供一个初始值。
 * 它可以用来作为全局静态数据共享的一种方式。
 */
ZBUS_CHAN_DEFINE(version_chan,       /* Name (通道名称) */
		 struct version_msg, /* Message type (消息类型) */
		 NULL,                 /* Validator (验证器函数，无) */
		 NULL,                 /* User data (用户自定义数据，无) */
		 ZBUS_OBSERVERS_EMPTY, /* observers (没有观察者) */
		 ZBUS_MSG_INIT(.major = 0, .minor = 1,
			       .build = 2) /* Initial value (通道内消息的初始值) */
);

/**
 * @brief 定义加速度数据通道 (acc_data_chan)
 * 
 * 这是该示例中最核心的通道。它被绑定了三个不同类型的观察者。
 * 当有人向该通道发布 (pub) 数据时，zbus 会负责通知这三个观察者。
 */
ZBUS_CHAN_DEFINE(acc_data_chan,  /* Name (通道名称) */
		 struct acc_msg, /* Message type (消息类型) */
		 NULL,                                            /* Validator (验证器函数，无) */
		 NULL,                                            /* User data (用户自定义数据，无) */
		 ZBUS_OBSERVERS(foo_lis, bar_sub, baz_async_lis), /* observers (列出将要接收通知的三个观察者) */
		 ZBUS_MSG_INIT(.x = 0, .y = 0, .z = 0)            /* Initial value (加速度初始值为 0) */
);

/**
 * @brief 简单数据验证器
 * 
 * @param msg 指向将要发布的消息数据的指针
 * @param msg_size 消息的大小
 * @return true 如果验证通过，允许发布
 * @return false 如果验证失败，zbus_chan_pub 将返回 -ENOMSG
 */
static bool simple_chan_validator(const void *msg, size_t msg_size)
{
	ARG_UNUSED(msg_size);

	const int *simple = msg;

	/* 业务规则：发布的数据必须在 0 到 9 之间 */
	if ((*simple >= 0) && (*simple < 10)) {
		return true;
	}

	return false;
}

/**
 * @brief 定义带验证器的简单通道
 */
ZBUS_CHAN_DEFINE(simple_chan, /* Name */
		 int,         /* Message type */
		 simple_chan_validator, /* Validator (挂载了上述验证函数) */
		 NULL,                  /* User data */
		 ZBUS_OBSERVERS_EMPTY,  /* observers */
		 0                      /* Initial value is 0 */
);

/**
 * @brief 同步监听器回调函数 (Listener Callback)
 * 
 * @warning 这个函数会在 `zbus_chan_pub` 的调用者线程上下文中直接同步执行！
 * 不能包含诸如 `k_sleep` 这种阻塞操作。
 * 
 * @param chan 触发回调的通道常量指针
 */
static void listener_callback_example(const struct zbus_channel *chan)
{
	/* 因为是在 pub 过程中，通道已被锁定，所以我们可以使用 zbus_chan_const_msg 进行安全的零拷贝访问 */
	const struct acc_msg *acc = zbus_chan_const_msg(chan);

	LOG_INF("From listener -> Acc x=%d, y=%d, z=%d", acc->x, acc->y, acc->z);
}

/**
 * @brief 将上述回调注册为 ZBUS 同步监听器 (名为 foo_lis)
 */
ZBUS_LISTENER_DEFINE(foo_lis, listener_callback_example);

/**
 * @brief 异步监听器回调函数 (Async Listener Callback)
 * 
 * 与同步监听器不同，它不阻塞发布者。它由系统工作队列(System Workqueue)调度执行。
 * 
 * @param chan 触发回调的通道常量指针
 * @param message 指向被 zbus 深度拷贝的消息副本的指针
 */
static void async_listener_callback_example(const struct zbus_channel *chan, const void *message)
{
	/* 注意这里使用的是系统传入的 message 副本指针，而不是直接去通道里读 */
	const struct acc_msg *acc = message;

	LOG_INF("From async listener -> Acc x=%d, y=%d, z=%d", acc->x, acc->y, acc->z);
}

/**
 * @brief 将上述回调注册为 ZBUS 异步监听器 (名为 baz_async_lis)
 */
ZBUS_ASYNC_LISTENER_DEFINE(baz_async_lis, async_listener_callback_example);

/**
 * @brief 定义一个 ZBUS 订阅者 (Subscriber)，名为 bar_sub
 *
 * 队列深度为 4。这意味着发布者可以连续发布 4 次通知放入队列中，而不会被阻塞。
 * 但请注意，队列里存的仅是通道的指针引用，而不是实际消息内容！
 */
ZBUS_SUBSCRIBER_DEFINE(bar_sub, 4);

/**
 * @brief 订阅者专用的业务处理线程
 *
 * 订阅者不同于回调，它需要一个实体线程来提取和处理消息队列中的通知。
 */
static void subscriber_task(void)
{
	const struct zbus_channel *chan;

	while (!zbus_sub_wait(&bar_sub, &chan, K_FOREVER)) {
		/* zbus_sub_wait 被唤醒，说明有通道发布了新数据 */
		struct acc_msg acc;

		/* 确认是我们要处理的那个通道 */
		if (&acc_data_chan == chan) {
			/* 主动从通道中将数据拷贝出来 (可能读到的是多次发布后的最终覆盖值) */
			zbus_chan_read(&acc_data_chan, &acc, K_MSEC(500));

			LOG_INF("From subscriber -> Acc x=%d, y=%d, z=%d", acc.x, acc.y, acc.z);
		}
	}
}

/* 创建并启动订阅者线程 */
K_THREAD_DEFINE(subscriber_task_id, CONFIG_MAIN_STACK_SIZE, subscriber_task, NULL, NULL, NULL, 3, 0,
		0);

/**
 * @brief 迭代器辅助函数：打印通道信息
 */
static bool print_channel_data_iterator(const struct zbus_channel *chan, void *user_data)
{
	int *count = user_data;

	LOG_INF("%d - Channel %s:", *count, zbus_chan_name(chan));
	LOG_INF("      Message size: %d", zbus_chan_msg_size(chan));
	LOG_INF("      Observers:");

	++(*count);

	struct zbus_channel_observation *observation;

	/* 遍历并打印挂载在这个通道上的所有静态观察者 */
	for (int16_t i = chan->data->observers_start_idx, limit = chan->data->observers_end_idx;
	     i < limit; ++i) {
		STRUCT_SECTION_GET(zbus_channel_observation, i, &observation);

		__ASSERT(observation != NULL, "observation must be not NULL");

		LOG_INF("      - %s", observation->obs->name);
	}

	struct zbus_observer_node *obs_nd, *tmp;

	/* 遍历并打印运行期动态添加的观察者 (本例为空) */
	SYS_SLIST_FOR_EACH_CONTAINER_SAFE(&chan->data->observers, obs_nd, tmp, node) {
		LOG_INF("      - %s", obs_nd->obs->name);
	}

	return true;
}

/**
 * @brief 迭代器辅助函数：打印观察者信息
 */
static bool print_observer_data_iterator(const struct zbus_observer *obs, void *user_data)
{
	int *count = user_data;

	LOG_INF("%d - %s %s", *count,
		obs->type == ZBUS_OBSERVER_LISTENER_TYPE ? "Listener" : "Subscriber",
		zbus_obs_name(obs));

	++(*count);

	return true;
}

int main(void)
{
	int err, value;
	struct acc_msg acc1 = {.x = 1, .y = 1, .z = 1};
	
	/* 1. 直接读取 version_chan 的初始静态数据 (零拷贝方式) */
	const struct version_msg *v = zbus_chan_const_msg(&version_chan);

	LOG_INF("Sensor sample started raw reading, version %u.%u-%u!", v->major, v->minor,
		v->build);

	int count = 0;

	/* 2. 使用迭代器自省功能：打印系统中所有的通道 */
	LOG_INF("Channel list:");
	zbus_iterate_over_channels_with_user_data(print_channel_data_iterator, &count);

	count = 0;

	/* 3. 使用迭代器自省功能：打印系统中所有的观察者 */
	LOG_INF("Observers list:");
	zbus_iterate_over_observers_with_user_data(print_observer_data_iterator, &count);
	
	/* 4. 执行核心操作：向 acc_data_chan 发布数据
	 * 这里将触发 VDED 调度引擎：
	 *  - 同步调用 foo_lis (Listener)
	 *  - 将通知发送给 bar_sub 的消息队列
	 *  - 将数据复本送入 baz_async_lis 并在工作队列中排队
	 */
	zbus_chan_pub(&acc_data_chan, &acc1, K_SECONDS(1));

	k_msleep(1000);

	acc1.x = 2;
	acc1.y = 2;
	acc1.z = 2;
	/* 再次发布更新数据 */
	zbus_chan_pub(&acc_data_chan, &(acc1), K_SECONDS(1));

	/* 5. 演示带 Validator 的通道拦截功能 */
	value = 5; /* 5 在 [0, 9] 范围内，有效 */
	err = zbus_chan_pub(&simple_chan, &value, K_MSEC(200));

	if (err == 0) {
		LOG_INF("Pub a valid value to a channel with validator successfully.");
	}

	value = 15; /* 15 超出范围，无效 */
	err = zbus_chan_pub(&simple_chan, &value, K_MSEC(200));

	if (err == -ENOMSG) {
		/* -ENOMSG 代表消息被 Validator 拦截拒绝 */
		LOG_INF("Pub an invalid value to a channel with validator successfully.");
	}
	
	return 0;
}
