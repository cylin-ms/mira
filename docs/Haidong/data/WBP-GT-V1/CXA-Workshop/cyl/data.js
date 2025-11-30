// GT3 Workshop - Ground Truth Tasks (24 tasks)
const gtTasks = [
    { key_date: "6/19", accountable: "Nicolle", milestone_activity: "Lock on agenda for 6/23 LT Planning or cancel meeting" },
    { key_date: "6/20", accountable: "Nicolle", milestone_activity: "Send agenda for 6/23 LT Planning" },
    { key_date: "6/23 EOD", accountable: "Nicolle/Diane", milestone_activity: "Lock on participants and update workshop invites" },
    { key_date: "6/23", accountable: "Nicolle", milestone_activity: "LT Planning session" },
    { key_date: "Wk of 6/23", accountable: "Nicolle/Diane", milestone_activity: "Plan all logistics for workshop" },
    { key_date: "Wk of 6/23", accountable: "Diane", milestone_activity: "Schedule 8/4 LT Workshop Output Review" },
    { key_date: "6/25", accountable: "Nicolle", milestone_activity: "Lock on agenda for 6/30 LT Planning or cancel meeting" },
    { key_date: "6/26", accountable: "Nicolle", milestone_activity: "Send agenda for 6/30 LT Planning" },
    { key_date: "6/30", accountable: "Nicolle", milestone_activity: "LT Planning session" },
    { key_date: "6/30", accountable: "Nicolle", milestone_activity: "Schedule v-Team meeting for Workshop Output working sessions" },
    { key_date: "7/7", accountable: "Nicolle/Diane", milestone_activity: "Physically check conf room and working equipment" },
    { key_date: "7/7", accountable: "Nicolle", milestone_activity: "Send pre-workshop communication to participants" },
    { key_date: "7/9", accountable: "Nicolle", milestone_activity: "Lock on agenda for 7/14 LT Planning or cancel meeting" },
    { key_date: "7/10", accountable: "Nicolle", milestone_activity: "Send agenda for 7/14 LT Planning" },
    { key_date: "7/14", accountable: "Nicolle", milestone_activity: "LT Planning session" },
    { key_date: "7/14", accountable: "Nicolle", milestone_activity: "Send final pre-workshop communication to participants" },
    { key_date: "7/14", accountable: "Nicolle, Maddie", milestone_activity: "Run-Dry with all facilitators" },
    { key_date: "7/15-7/17", accountable: "Nicolle", milestone_activity: "KM Workshop Event" },
    { key_date: "7/21", accountable: "Diane", milestone_activity: "Post recording and materials in CXA SharePoint site" },
    { key_date: "7/21", accountable: "Nicolle", milestone_activity: "Send Thank You communication to workshop participants" },
    { key_date: "7/21", accountable: "Nicolle", milestone_activity: "Rough draft of Workshop Output ready for v-team review" },
    { key_date: "7/22-7/25", accountable: "Nicolle", milestone_activity: "V-team finalizes Workshop Output ready for LT review" },
    { key_date: "7/28", accountable: "Nicolle", milestone_activity: "Agenda and pre-read goes out for 8/4 LT Workshop Output Review" },
    { key_date: "8/4", accountable: "Nicolle", milestone_activity: "LT Workshop Output Review Meeting" }
];

// All 46 assertions with task_indices for 100% coverage
const assertions = [
    { assertion_id: "GT3_S1", dimension: "S1", dimension_name: "Meeting Details", level: "critical", template: "The plan should reference the event [EVENT_NAME] scheduled for [EVENT_DATE].", instantiated: "The plan should reference the event 'Knowledge Management Workshop' scheduled for July 15-17, 2025.", linked_g_dims: ["G3", "G5"], g_slots: [{g_dim:"G5",slot_type:"EVENT_NAME",value:"Knowledge Management Workshop"},{g_dim:"G3",slot_type:"EVENT_DATE",value:"July 15-17, 2025"}], task_indices: [17] },
    { assertion_id: "GT3_S2", dimension: "S2", dimension_name: "Timeline Alignment", level: "critical", template: "The plan should sequence tasks from [START_DATE] through [END_DATE].", instantiated: "The plan should sequence tasks from 6/19 through 8/4, covering pre-event preparation, event execution (7/15-7/17), and post-event follow-up.", linked_g_dims: ["G3"], g_slots: [{g_dim:"G3",slot_type:"START_DATE",value:"6/19"},{g_dim:"G3",slot_type:"END_DATE",value:"8/4"}], task_indices: [] },
    { assertion_id: "GT3_S3_01", dimension: "S3", dimension_name: "Ownership Assignment", level: "critical", template: "Task [TASK] should be assigned to [OWNER].", instantiated: "Task 'Lock on agenda for 6/23 LT Planning' should be assigned to Nicolle.", linked_g_dims: ["G2", "G6"], g_slots: [{g_dim:"G2",slot_type:"OWNER",value:"Nicolle"},{g_dim:"G6",slot_type:"TASK",value:"Lock on agenda for 6/23 LT Planning"}], task_indices: [0] },
    { assertion_id: "GT3_S3_02", dimension: "S3", dimension_name: "Ownership Assignment", level: "critical", template: "Task [TASK] should be assigned to [OWNER].", instantiated: "Task 'Lock on participants' should be assigned to Nicolle/Diane.", linked_g_dims: ["G2", "G6"], g_slots: [{g_dim:"G2",slot_type:"OWNER",value:"Nicolle/Diane"},{g_dim:"G6",slot_type:"TASK",value:"Lock on participants"}], task_indices: [2] },
    { assertion_id: "GT3_S3_03", dimension: "S3", dimension_name: "Ownership Assignment", level: "critical", template: "Task [TASK] should be assigned to [OWNER].", instantiated: "Task 'Plan all logistics for workshop' should be assigned to Nicolle/Diane.", linked_g_dims: ["G2", "G6"], g_slots: [{g_dim:"G2",slot_type:"OWNER",value:"Nicolle/Diane"},{g_dim:"G6",slot_type:"TASK",value:"Plan all logistics"}], task_indices: [4] },
    { assertion_id: "GT3_S3_04", dimension: "S3", dimension_name: "Ownership Assignment", level: "critical", template: "Task [TASK] should be assigned to [OWNER].", instantiated: "Task 'Schedule 8/4 LT Workshop Output Review' should be assigned to Diane.", linked_g_dims: ["G2", "G6"], g_slots: [{g_dim:"G2",slot_type:"OWNER",value:"Diane"},{g_dim:"G6",slot_type:"TASK",value:"Schedule 8/4 LT Workshop Output Review"}], task_indices: [5] },
    { assertion_id: "GT3_S3_05", dimension: "S3", dimension_name: "Ownership Assignment", level: "critical", template: "Task [TASK] should be assigned to [OWNER].", instantiated: "Task 'Physically check conf room' should be assigned to Nicolle/Diane.", linked_g_dims: ["G2", "G6"], g_slots: [{g_dim:"G2",slot_type:"OWNER",value:"Nicolle/Diane"},{g_dim:"G6",slot_type:"TASK",value:"Physically check conf room"}], task_indices: [10] },
    { assertion_id: "GT3_S3_06", dimension: "S3", dimension_name: "Ownership Assignment", level: "critical", template: "Task [TASK] should be assigned to [OWNER].", instantiated: "Task 'Send pre-workshop communication' should be assigned to Nicolle.", linked_g_dims: ["G2", "G6"], g_slots: [{g_dim:"G2",slot_type:"OWNER",value:"Nicolle"},{g_dim:"G6",slot_type:"TASK",value:"Send pre-workshop communication"}], task_indices: [11] },
    { assertion_id: "GT3_S3_07", dimension: "S3", dimension_name: "Ownership Assignment", level: "critical", template: "Task [TASK] should be assigned to [OWNER].", instantiated: "Task 'Run-Dry with all facilitators' should be assigned to Nicolle, Maddie.", linked_g_dims: ["G2", "G6"], g_slots: [{g_dim:"G2",slot_type:"OWNER",value:"Nicolle, Maddie"},{g_dim:"G6",slot_type:"TASK",value:"Run-Dry with all facilitators"}], task_indices: [16] },
    { assertion_id: "GT3_S3_08", dimension: "S3", dimension_name: "Ownership Assignment", level: "critical", template: "Task [TASK] should be assigned to [OWNER].", instantiated: "Task 'KM Workshop Event' should be assigned to Nicolle.", linked_g_dims: ["G2", "G6"], g_slots: [{g_dim:"G2",slot_type:"OWNER",value:"Nicolle"},{g_dim:"G6",slot_type:"TASK",value:"KM Workshop Event"}], task_indices: [17] },
    { assertion_id: "GT3_S3_09", dimension: "S3", dimension_name: "Ownership Assignment", level: "expected", template: "Task [TASK] should be assigned to [OWNER].", instantiated: "Task 'Post recording and materials' should be assigned to Diane.", linked_g_dims: ["G2", "G6"], g_slots: [{g_dim:"G2",slot_type:"OWNER",value:"Diane"},{g_dim:"G6",slot_type:"TASK",value:"Post recording and materials"}], task_indices: [18] },
    { assertion_id: "GT3_S3_10", dimension: "S3", dimension_name: "Ownership Assignment", level: "expected", template: "Task [TASK] should be assigned to [OWNER].", instantiated: "Task 'Send Thank You communication' should be assigned to Nicolle.", linked_g_dims: ["G2", "G6"], g_slots: [{g_dim:"G2",slot_type:"OWNER",value:"Nicolle"},{g_dim:"G6",slot_type:"TASK",value:"Send Thank You communication"}], task_indices: [19] },
    { assertion_id: "GT3_S3_11", dimension: "S3", dimension_name: "Ownership Assignment", level: "expected", template: "Task [TASK] should be assigned to [OWNER].", instantiated: "Task 'LT Workshop Output Review Meeting' should be assigned to Nicolle.", linked_g_dims: ["G2", "G6"], g_slots: [{g_dim:"G2",slot_type:"OWNER",value:"Nicolle"},{g_dim:"G6",slot_type:"TASK",value:"LT Workshop Output Review Meeting"}], task_indices: [23] },
    { assertion_id: "GT3_S3_12", dimension: "S3", dimension_name: "Ownership Assignment", level: "expected", template: "Task [TASK] should be assigned to [OWNER].", instantiated: "Task 'Send agenda for 6/23 LT Planning' should be assigned to Nicolle.", linked_g_dims: ["G2", "G6"], g_slots: [{g_dim:"G2",slot_type:"OWNER",value:"Nicolle"},{g_dim:"G6",slot_type:"TASK",value:"Send agenda for 6/23 LT Planning"}], task_indices: [1] },
    { assertion_id: "GT3_S3_13", dimension: "S3", dimension_name: "Ownership Assignment", level: "expected", template: "Task [TASK] should be assigned to [OWNER].", instantiated: "Task 'Lock on agenda for 6/30 LT Planning' should be assigned to Nicolle.", linked_g_dims: ["G2", "G6"], g_slots: [{g_dim:"G2",slot_type:"OWNER",value:"Nicolle"},{g_dim:"G6",slot_type:"TASK",value:"Lock on agenda for 6/30 LT Planning"}], task_indices: [6] },
    { assertion_id: "GT3_S3_14", dimension: "S3", dimension_name: "Ownership Assignment", level: "expected", template: "Task [TASK] should be assigned to [OWNER].", instantiated: "Task 'Send agenda for 6/30 LT Planning' should be assigned to Nicolle.", linked_g_dims: ["G2", "G6"], g_slots: [{g_dim:"G2",slot_type:"OWNER",value:"Nicolle"},{g_dim:"G6",slot_type:"TASK",value:"Send agenda for 6/30 LT Planning"}], task_indices: [7] },
    { assertion_id: "GT3_S3_15", dimension: "S3", dimension_name: "Ownership Assignment", level: "expected", template: "Task [TASK] should be assigned to [OWNER].", instantiated: "Task 'Schedule v-Team meeting' should be assigned to Nicolle.", linked_g_dims: ["G2", "G6"], g_slots: [{g_dim:"G2",slot_type:"OWNER",value:"Nicolle"},{g_dim:"G6",slot_type:"TASK",value:"Schedule v-Team meeting"}], task_indices: [9] },
    { assertion_id: "GT3_S3_16", dimension: "S3", dimension_name: "Ownership Assignment", level: "expected", template: "Task [TASK] should be assigned to [OWNER].", instantiated: "Task 'Lock on agenda for 7/14 LT Planning' should be assigned to Nicolle.", linked_g_dims: ["G2", "G6"], g_slots: [{g_dim:"G2",slot_type:"OWNER",value:"Nicolle"},{g_dim:"G6",slot_type:"TASK",value:"Lock on agenda for 7/14 LT Planning"}], task_indices: [12] },
    { assertion_id: "GT3_S3_17", dimension: "S3", dimension_name: "Ownership Assignment", level: "expected", template: "Task [TASK] should be assigned to [OWNER].", instantiated: "Task 'Send agenda for 7/14 LT Planning' should be assigned to Nicolle.", linked_g_dims: ["G2", "G6"], g_slots: [{g_dim:"G2",slot_type:"OWNER",value:"Nicolle"},{g_dim:"G6",slot_type:"TASK",value:"Send agenda for 7/14 LT Planning"}], task_indices: [13] },
    { assertion_id: "GT3_S3_18", dimension: "S3", dimension_name: "Ownership Assignment", level: "expected", template: "Task [TASK] should be assigned to [OWNER].", instantiated: "Task 'Send final pre-workshop communication' should be assigned to Nicolle.", linked_g_dims: ["G2", "G6"], g_slots: [{g_dim:"G2",slot_type:"OWNER",value:"Nicolle"},{g_dim:"G6",slot_type:"TASK",value:"Send final pre-workshop communication"}], task_indices: [15] },
    { assertion_id: "GT3_S3_19", dimension: "S3", dimension_name: "Ownership Assignment", level: "expected", template: "Task [TASK] should be assigned to [OWNER].", instantiated: "Task 'Rough draft of Workshop Output' should be assigned to Nicolle.", linked_g_dims: ["G2", "G6"], g_slots: [{g_dim:"G2",slot_type:"OWNER",value:"Nicolle"},{g_dim:"G6",slot_type:"TASK",value:"Rough draft of Workshop Output"}], task_indices: [20] },
    { assertion_id: "GT3_S3_20", dimension: "S3", dimension_name: "Ownership Assignment", level: "expected", template: "Task [TASK] should be assigned to [OWNER].", instantiated: "Task 'Agenda and pre-read goes out' should be assigned to Nicolle.", linked_g_dims: ["G2", "G6"], g_slots: [{g_dim:"G2",slot_type:"OWNER",value:"Nicolle"},{g_dim:"G6",slot_type:"TASK",value:"Agenda and pre-read goes out"}], task_indices: [22] },
    { assertion_id: "GT3_S5_01", dimension: "S5", dimension_name: "Task Dates", level: "critical", template: "Task [TASK] should have due date [DUE_DATE].", instantiated: "Task 'Lock on agenda for 6/23 LT Planning' should have due date 6/19.", linked_g_dims: ["G3", "G6"], g_slots: [{g_dim:"G3",slot_type:"DUE_DATE",value:"6/19"},{g_dim:"G6",slot_type:"TASK",value:"Lock on agenda for 6/23 LT Planning"}], task_indices: [0] },
    { assertion_id: "GT3_S5_02", dimension: "S5", dimension_name: "Task Dates", level: "critical", template: "Task [TASK] should have due date [DUE_DATE].", instantiated: "Task 'Lock on participants' should have due date 6/23 EOD.", linked_g_dims: ["G3", "G6"], g_slots: [{g_dim:"G3",slot_type:"DUE_DATE",value:"6/23 EOD"},{g_dim:"G6",slot_type:"TASK",value:"Lock on participants"}], task_indices: [2] },
    { assertion_id: "GT3_S5_03", dimension: "S5", dimension_name: "Task Dates", level: "critical", template: "Task [TASK] should have due date [DUE_DATE].", instantiated: "Task 'Physically check conf room' should have due date 7/7.", linked_g_dims: ["G3", "G6"], g_slots: [{g_dim:"G3",slot_type:"DUE_DATE",value:"7/7"},{g_dim:"G6",slot_type:"TASK",value:"Physically check conf room"}], task_indices: [10] },
    { assertion_id: "GT3_S5_04", dimension: "S5", dimension_name: "Task Dates", level: "critical", template: "Task [TASK] should have due date [DUE_DATE].", instantiated: "Task 'Run-Dry with all facilitators' should have due date 7/14.", linked_g_dims: ["G3", "G6"], g_slots: [{g_dim:"G3",slot_type:"DUE_DATE",value:"7/14"},{g_dim:"G6",slot_type:"TASK",value:"Run-Dry with all facilitators"}], task_indices: [16] },
    { assertion_id: "GT3_S5_05", dimension: "S5", dimension_name: "Task Dates", level: "critical", template: "Task [TASK] should have due date [DUE_DATE].", instantiated: "Task 'KM Workshop Event' should have due date 7/15-7/17.", linked_g_dims: ["G3", "G6"], g_slots: [{g_dim:"G3",slot_type:"DUE_DATE",value:"7/15-7/17"},{g_dim:"G6",slot_type:"TASK",value:"KM Workshop Event"}], task_indices: [17] },
    { assertion_id: "GT3_S5_06", dimension: "S5", dimension_name: "Task Dates", level: "expected", template: "Task [TASK] should have due date [DUE_DATE].", instantiated: "Task 'Post recording and materials' should have due date 7/21.", linked_g_dims: ["G3", "G6"], g_slots: [{g_dim:"G3",slot_type:"DUE_DATE",value:"7/21"},{g_dim:"G6",slot_type:"TASK",value:"Post recording and materials"}], task_indices: [18] },
    { assertion_id: "GT3_S5_07", dimension: "S5", dimension_name: "Task Dates", level: "expected", template: "Task [TASK] should have due date [DUE_DATE].", instantiated: "Task 'V-team finalizes Workshop Output' should have due date 7/22-7/25.", linked_g_dims: ["G3", "G6"], g_slots: [{g_dim:"G3",slot_type:"DUE_DATE",value:"7/22-7/25"},{g_dim:"G6",slot_type:"TASK",value:"V-team finalizes Workshop Output"}], task_indices: [21] },
    { assertion_id: "GT3_S5_08", dimension: "S5", dimension_name: "Task Dates", level: "expected", template: "Task [TASK] should have due date [DUE_DATE].", instantiated: "Task 'LT Workshop Output Review Meeting' should have due date 8/4.", linked_g_dims: ["G3", "G6"], g_slots: [{g_dim:"G3",slot_type:"DUE_DATE",value:"8/4"},{g_dim:"G6",slot_type:"TASK",value:"LT Workshop Output Review Meeting"}], task_indices: [23] },
    { assertion_id: "GT3_S5_09", dimension: "S5", dimension_name: "Task Dates", level: "expected", template: "Task [TASK] should have due date [DUE_DATE].", instantiated: "Task 'Send agenda for 6/23 LT Planning' should have due date 6/20.", linked_g_dims: ["G3", "G6"], g_slots: [{g_dim:"G3",slot_type:"DUE_DATE",value:"6/20"},{g_dim:"G6",slot_type:"TASK",value:"Send agenda for 6/23 LT Planning"}], task_indices: [1] },
    { assertion_id: "GT3_S5_10", dimension: "S5", dimension_name: "Task Dates", level: "expected", template: "Task [TASK] should have due date [DUE_DATE].", instantiated: "Task 'Lock on agenda for 6/30 LT Planning' should have due date 6/25.", linked_g_dims: ["G3", "G6"], g_slots: [{g_dim:"G3",slot_type:"DUE_DATE",value:"6/25"},{g_dim:"G6",slot_type:"TASK",value:"Lock on agenda for 6/30 LT Planning"}], task_indices: [6] },
    { assertion_id: "GT3_S5_11", dimension: "S5", dimension_name: "Task Dates", level: "expected", template: "Task [TASK] should have due date [DUE_DATE].", instantiated: "Task 'Send agenda for 6/30 LT Planning' should have due date 6/26.", linked_g_dims: ["G3", "G6"], g_slots: [{g_dim:"G3",slot_type:"DUE_DATE",value:"6/26"},{g_dim:"G6",slot_type:"TASK",value:"Send agenda for 6/30 LT Planning"}], task_indices: [7] },
    { assertion_id: "GT3_S5_12", dimension: "S5", dimension_name: "Task Dates", level: "expected", template: "Task [TASK] should have due date [DUE_DATE].", instantiated: "Task 'Schedule v-Team meeting' should have due date 6/30.", linked_g_dims: ["G3", "G6"], g_slots: [{g_dim:"G3",slot_type:"DUE_DATE",value:"6/30"},{g_dim:"G6",slot_type:"TASK",value:"Schedule v-Team meeting"}], task_indices: [9] },
    { assertion_id: "GT3_S5_13", dimension: "S5", dimension_name: "Task Dates", level: "expected", template: "Task [TASK] should have due date [DUE_DATE].", instantiated: "Task 'Lock on agenda for 7/14 LT Planning' should have due date 7/9.", linked_g_dims: ["G3", "G6"], g_slots: [{g_dim:"G3",slot_type:"DUE_DATE",value:"7/9"},{g_dim:"G6",slot_type:"TASK",value:"Lock on agenda for 7/14 LT Planning"}], task_indices: [12] },
    { assertion_id: "GT3_S5_14", dimension: "S5", dimension_name: "Task Dates", level: "expected", template: "Task [TASK] should have due date [DUE_DATE].", instantiated: "Task 'Send agenda for 7/14 LT Planning' should have due date 7/10.", linked_g_dims: ["G3", "G6"], g_slots: [{g_dim:"G3",slot_type:"DUE_DATE",value:"7/10"},{g_dim:"G6",slot_type:"TASK",value:"Send agenda for 7/14 LT Planning"}], task_indices: [13] },
    { assertion_id: "GT3_S5_15", dimension: "S5", dimension_name: "Task Dates", level: "expected", template: "Task [TASK] should have due date [DUE_DATE].", instantiated: "Task 'Send final pre-workshop communication' should have due date 7/14.", linked_g_dims: ["G3", "G6"], g_slots: [{g_dim:"G3",slot_type:"DUE_DATE",value:"7/14"},{g_dim:"G6",slot_type:"TASK",value:"Send final pre-workshop communication"}], task_indices: [15] },
    { assertion_id: "GT3_S5_16", dimension: "S5", dimension_name: "Task Dates", level: "expected", template: "Task [TASK] should have due date [DUE_DATE].", instantiated: "Task 'Rough draft of Workshop Output' should have due date 7/21.", linked_g_dims: ["G3", "G6"], g_slots: [{g_dim:"G3",slot_type:"DUE_DATE",value:"7/21"},{g_dim:"G6",slot_type:"TASK",value:"Rough draft of Workshop Output"}], task_indices: [20] },
    { assertion_id: "GT3_S5_17", dimension: "S5", dimension_name: "Task Dates", level: "expected", template: "Task [TASK] should have due date [DUE_DATE].", instantiated: "Task 'Agenda and pre-read goes out' should have due date 7/28.", linked_g_dims: ["G3", "G6"], g_slots: [{g_dim:"G3",slot_type:"DUE_DATE",value:"7/28"},{g_dim:"G6",slot_type:"TASK",value:"Agenda and pre-read goes out"}], task_indices: [22] },
    { assertion_id: "GT3_S9_01", dimension: "S9", dimension_name: "Checkpoints", level: "expected", template: "The plan should include checkpoint [CHECKPOINT] on [DUE_DATE].", instantiated: "The plan should include checkpoint 'LT Planning session' on 6/23 owned by Nicolle.", linked_g_dims: ["G2", "G3", "G6"], g_slots: [{g_dim:"G2",slot_type:"OWNER",value:"Nicolle"},{g_dim:"G3",slot_type:"DUE_DATE",value:"6/23"},{g_dim:"G6",slot_type:"CHECKPOINT",value:"LT Planning session"}], task_indices: [3] },
    { assertion_id: "GT3_S9_02", dimension: "S9", dimension_name: "Checkpoints", level: "expected", template: "The plan should include checkpoint [CHECKPOINT] on [DUE_DATE].", instantiated: "The plan should include checkpoint 'LT Planning session' on 6/30 owned by Nicolle.", linked_g_dims: ["G2", "G3", "G6"], g_slots: [{g_dim:"G2",slot_type:"OWNER",value:"Nicolle"},{g_dim:"G3",slot_type:"DUE_DATE",value:"6/30"},{g_dim:"G6",slot_type:"CHECKPOINT",value:"LT Planning session"}], task_indices: [8] },
    { assertion_id: "GT3_S9_03", dimension: "S9", dimension_name: "Checkpoints", level: "expected", template: "The plan should include checkpoint [CHECKPOINT] on [DUE_DATE].", instantiated: "The plan should include checkpoint 'LT Planning session' on 7/14 owned by Nicolle.", linked_g_dims: ["G2", "G3", "G6"], g_slots: [{g_dim:"G2",slot_type:"OWNER",value:"Nicolle"},{g_dim:"G3",slot_type:"DUE_DATE",value:"7/14"},{g_dim:"G6",slot_type:"CHECKPOINT",value:"LT Planning session"}], task_indices: [14] },
    { assertion_id: "GT3_S18_01", dimension: "S18", dimension_name: "Post-Event Actions", level: "expected", template: "The plan should include post-event task [TASK] on [DUE_DATE].", instantiated: "The plan should include post-event task 'Post recording and materials' assigned to Diane on 7/21.", linked_g_dims: ["G2", "G3", "G6"], g_slots: [{g_dim:"G2",slot_type:"OWNER",value:"Diane"},{g_dim:"G3",slot_type:"DUE_DATE",value:"7/21"},{g_dim:"G6",slot_type:"TASK",value:"Post recording and materials"}], task_indices: [18] },
    { assertion_id: "GT3_S18_02", dimension: "S18", dimension_name: "Post-Event Actions", level: "expected", template: "The plan should include post-event task [TASK] on [DUE_DATE].", instantiated: "The plan should include post-event task 'Send Thank You communication' assigned to Nicolle on 7/21.", linked_g_dims: ["G2", "G3", "G6"], g_slots: [{g_dim:"G2",slot_type:"OWNER",value:"Nicolle"},{g_dim:"G3",slot_type:"DUE_DATE",value:"7/21"},{g_dim:"G6",slot_type:"TASK",value:"Send Thank You communication"}], task_indices: [19] },
    { assertion_id: "GT3_S18_03", dimension: "S18", dimension_name: "Post-Event Actions", level: "expected", template: "The plan should include post-event task [TASK] on [DUE_DATE].", instantiated: "The plan should include post-event task 'LT Workshop Output Review Meeting' assigned to Nicolle on 8/4.", linked_g_dims: ["G2", "G3", "G6"], g_slots: [{g_dim:"G2",slot_type:"OWNER",value:"Nicolle"},{g_dim:"G3",slot_type:"DUE_DATE",value:"8/4"},{g_dim:"G6",slot_type:"TASK",value:"LT Workshop Output Review Meeting"}], task_indices: [23] },
    { assertion_id: "GT3_S20", dimension: "S20", dimension_name: "Clarity & First Impression", level: "expected", template: "The plan should be presented in a clear table format with columns: [COLUMNS].", instantiated: "The plan should be presented in a clear table format with columns: Key Date, Accountable, Milestone Activity.", linked_g_dims: ["G7"], g_slots: [{g_dim:"G7",slot_type:"COLUMNS",value:"Key Date, Accountable, Milestone Activity"}], task_indices: [] }
];

// Build task coverage map
const taskCoverage = new Map();
assertions.forEach(a => { if (a.task_indices) a.task_indices.forEach(idx => { if (!taskCoverage.has(idx)) taskCoverage.set(idx, []); taskCoverage.get(idx).push(a.assertion_id); }); });

// Render WBP table
function renderWbpTable() {
    const tbody = document.getElementById('wbp-body');
    tbody.innerHTML = gtTasks.map((task, idx) => {
        const isCovered = taskCoverage.has(idx);
        return `<tr id="task-row-${idx}" class="${isCovered ? 'covered' : 'not-covered'}"><td><span class="task-index ${isCovered ? 'covered' : 'not-covered'}">${idx + 1}</span></td><td>${task.key_date}</td><td>${task.accountable}</td><td>${task.milestone_activity}</td></tr>`;
    }).join('');
    document.getElementById('task-coverage').textContent = `${taskCoverage.size}/${gtTasks.length}`;
    const pct = Math.round((taskCoverage.size / gtTasks.length) * 100);
    document.getElementById('coverage-badge').textContent = `${pct}% Coverage`;
    document.getElementById('coverage-badge').className = 'coverage-badge ' + (pct === 100 ? 'coverage-full' : 'coverage-partial');
    const taskFilter = document.getElementById('filter-task');
    gtTasks.forEach((task, idx) => { const opt = document.createElement('option'); opt.value = idx; opt.textContent = `${idx + 1}. ${task.milestone_activity.substring(0, 30)}...`; taskFilter.appendChild(opt); });
}

function highlightTask(taskIndex) {
    document.querySelectorAll('.wbp-table tr').forEach(tr => tr.classList.remove('highlight'));
    const row = document.getElementById(`task-row-${taskIndex}`);
    if (row) { row.classList.add('highlight'); row.scrollIntoView({ behavior: 'smooth', block: 'center' }); }
}

function renderAssertions(filteredAssertions) {
    const container = document.getElementById('assertions-container');
    const emptyState = document.getElementById('empty-state');
    if (filteredAssertions.length === 0) { container.innerHTML = ''; emptyState.style.display = 'block'; document.getElementById('visible-count').textContent = '0'; return; }
    emptyState.style.display = 'none';
    document.getElementById('visible-count').textContent = filteredAssertions.length;
    container.innerHTML = filteredAssertions.map(a => `
        <div class="assertion-card level-${a.level}">
            <div class="card-header"><div><span class="assertion-id">${a.assertion_id}</span><div class="dimension-name">${a.dimension_name}</div></div><div style="display:flex;align-items:center;gap:8px"><span class="dimension-badge">${a.dimension}</span><span class="level-badge">${a.level}</span></div></div>
            <div class="assertion-template">${a.template}</div>
            <div class="assertion-text">${a.instantiated}</div>
            ${a.task_indices && a.task_indices.length > 0 ? `<div>${a.task_indices.map(idx => `<a href="#task-row-${idx}" class="task-link" onclick="highlightTask(${idx});return false;">Task ${idx + 1} →</a>`).join('')}</div>` : ''}
            ${a.g_slots && a.g_slots.length > 0 ? `<div class="slots-section"><div class="slots-header">Grounding Slots</div><div class="slot-tags">${a.g_slots.map(s => `<span class="slot-tag ${s.g_dim.toLowerCase()}"><span class="slot-dim ${s.g_dim.toLowerCase()}">${s.g_dim}</span><span class="slot-type">${s.slot_type}:</span><span class="slot-value" title="${s.value}">${s.value}</span></span>`).join('')}</div></div>` : ''}
            ${a.linked_g_dims && a.linked_g_dims.length > 0 ? `<div class="g-dims"><div class="g-dims-label">Linked G Dimensions</div>${a.linked_g_dims.map(g => `<span class="g-dim-tag">${g}</span>`).join('')}</div>` : ''}
        </div>
    `).join('');
}

function setupFilters() {
    const dimensions = [...new Set(assertions.map(a => a.dimension))].sort();
    const dimFilter = document.getElementById('filter-dimension');
    dimensions.forEach(dim => { const name = assertions.find(a => a.dimension === dim)?.dimension_name || dim; const opt = document.createElement('option'); opt.value = dim; opt.textContent = `${dim} - ${name}`; dimFilter.appendChild(opt); });
    const applyFilters = () => {
        const dimVal = document.getElementById('filter-dimension').value;
        const levelVal = document.getElementById('filter-level').value;
        const searchVal = document.getElementById('filter-search').value.toLowerCase();
        const taskVal = document.getElementById('filter-task').value;
        let filtered = assertions.filter(a => {
            if (dimVal && a.dimension !== dimVal) return false;
            if (levelVal && a.level !== levelVal) return false;
            if (searchVal && !a.instantiated.toLowerCase().includes(searchVal) && !a.template.toLowerCase().includes(searchVal)) return false;
            if (taskVal !== '' && (!a.task_indices || !a.task_indices.includes(parseInt(taskVal)))) return false;
            return true;
        });
        renderAssertions(filtered);
    };
    document.getElementById('filter-dimension').addEventListener('change', applyFilters);
    document.getElementById('filter-level').addEventListener('change', applyFilters);
    document.getElementById('filter-search').addEventListener('input', applyFilters);
    document.getElementById('filter-task').addEventListener('change', applyFilters);
}

// Initialize
renderWbpTable();
renderAssertions(assertions);
setupFilters();
