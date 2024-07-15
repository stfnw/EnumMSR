#include <asm/msr.h>
#include <linux/kernel.h>
#include <linux/module.h>

/* Enumerate all Model-Specific Registers (MSRs) on the current CPU (Intel-only). */

#define MSR_START 0x00000000
#define MSR_END 0xffffffff
#define MSR_LOG_STEP 0x00100000

static int __init mod_enum_msrs_init(void)
{
    pr_info("MSR Enumerator Module Loaded\n");

    u32 msr_nr_identified = 0; // count identified valid MSRs

    for (u32 msr = MSR_START;; msr++)
    {
        if (msr % MSR_LOG_STEP == 0)
            pr_info("Trying msr #0x%08x out of 0x%08x\n", msr, MSR_END);

        u64 res;
        if (rdmsrl_safe(msr, &res) == 0)
        {
            msr_nr_identified += 1;
            bool rw = !wrmsrl_safe(msr, res);
            pr_info("MSR 0x%08X (found %12d MSRs so far): 0x%016llx (%s)\n", msr, msr_nr_identified, res,
                    rw ? "read/write" : "read-only");
        }
        else
        {
            pr_debug("Failed to read MSR 0x%08X\n", msr);
        }

        cond_resched(); // be nicer to other tasks to be done

        // break is here and not in for-loop in order to not
        // overflow/wrap-around u32 which results in an infinite loop
        if (msr >= MSR_END)
            break;
    }

    return 0;
}

static void __exit mod_enum_msrs_exit(void)
{
    pr_info("MSR Enumerator Module Unloaded\n");
}

module_init(mod_enum_msrs_init);
module_exit(mod_enum_msrs_exit);

MODULE_LICENSE("GPL");
MODULE_AUTHOR("stfnw");
MODULE_VERSION("1.0");
MODULE_DESCRIPTION("A module to enumerate MSRs by iterating through all "
                   "possible 32-bit values");
