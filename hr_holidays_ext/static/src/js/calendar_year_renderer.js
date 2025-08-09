/** @odoo-module **/


// import {getColor} from "../colors";
import { patch } from "@web/core/utils/patch";
import { CalendarYearRenderer } from "@web/views/calendar/calendar_year/calendar_year_renderer";
import { getColor } from "@web/views/calendar/colors";


patch(
    CalendarYearRenderer.prototype,
    {
        onEventRender(info) {
            const {el, event} = info;
            el.dataset.eventId = event.id;
            el.classList.add("o_event");
            const record = this.props.model.records[event.id];
            if (record) {
                const color = getColor(record.colorIndex);
                if (typeof color === "string") {
                    el.style.backgroundColor = color;
                } else if (typeof color === "number") {
                    el.classList.add(`o_calendar_color_${color}`);
                } else {
                    el.classList.add("o_calendar_color_0");
                }
    
                if (record.isHatched) {
                    el.classList.add("o_event_hatched_yearly");
                }
    
                if (record.isStriked) {
                    // console.log("here")
                    el.classList.add("o_event_striked_yearly");
                }
                
            }
        }

    }
  );

