# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import timedelta
from dateutil import relativedelta
from datetime import datetime
import logging
_logger = logging.getLogger(__name__)

rec = 0
def autoIncrement():
    global rec
    pStart = 1
    pInterval = 1
    if rec == 0:
        rec = pStart
    else:
        rec += pInterval
    return rec


class DiscrepancyModel(models.TransientModel):
    _name = 'mto.discrepancy.report'
    _description = 'Discrepancy Report'

    @api.model
    def get_html(self):
        result = {}
        rcontext = {}
        context = dict(self.env.context)
        active_id = context.get('active_id', False)
        active_model = context.get('model', False)
        _logger.info(active_id)
        _logger.info(active_model)
        if active_id and active_model:
            rcontext['so_parent_date'] = "Date Discrepancy Report " + self.get_so_information()
            rcontext['so_parent_q'] = "Quantity Discrepancy Report " + self.get_so_information()
            rcontext['lines'] = self.get_so_line_discrepancy_report("date")
            rcontext['qlines'] = self.get_so_line_discrepancy_report("quantity")
            # _logger.info(rcontext['lines'])
            result['date_html'] = self.env.ref('syray_discrepancy_report.report_discrepancy_view').render(rcontext)
            result['quantity_html'] = self.env.ref('syray_discrepancy_report.report_discrepancy_view_quantity').render(rcontext)
            result['html'] = result['date_html'] + result['quantity_html']
            return result

    @api.model
    def get_so_information(self):
        discrepancy_list_data = []
        context = dict(self.env.context)
        active_id = context.get('active_id', False)
        active_model = context.get('model', False)
        so_data = self.env[active_model].browse(active_id)
        _logger.info(so_data)
        name = so_data.name
        if active_model == "sale.order.line":
            name = "(" + so_data.order_id.name + ") - " + name
        return name

    @api.model
    def get_so_line_discrepancy_report(self, sector):
        discrepancy_list_data = []
        context = dict(self.env.context)
        active_id = context.get('active_id', False)
        active_model = context.get('model', False)
        node_id = self.env[active_model].browse(active_id).node_id
        _logger.info(node_id)
        nodes = node_id.child_ids;
        for node in nodes:
            node_id = node.id
            _logger.info(node_id)
            res_model = node.res_model
            _logger.info(res_model)
            if res_model == "mrp.production" and sector == "date":
                discrepancy_list_data = self._recursive_node(node, discrepancy_list_data)
            elif res_model == "mrp.production" and sector == "quantity":
                discrepancy_list_data = self._quantity_recursive_node(node, discrepancy_list_data)
        # _logger.info(discrepancy_list_data)
        if sector == "date":
            lines = self._list_to_date_lines(discrepancy_list_data)
        else:
            lines = self._list_to_quantity_lines(discrepancy_list_data)
            # _logger.info(lines)
        return lines

    @api.model
    def _list_to_date_lines(self, discrepancy_list_data):
        lines = []
        _logger.info("in _list_to_lines")
        for data in discrepancy_list_data:
            lines.append({
                'id': autoIncrement(),
                'model': data['res_model'],
                'model_id': data['res_id'],
                'source_doc_name': data['source_doc_name'],
                'work_center': data.get('work_center', False),
                'is_used': True,
                'discrepancy_message_start': data.get('discrepancy_message_start', False),
                'discrepancy_message_end': data.get('discrepancy_message_end', False),
                'discrepancy_start_status': data.get('discrepancy_start_status', False),
                'discrepancy_finish_status': data.get('discrepancy_finish_status', False),
                'reference': data.get('reference_id', False),
                'res_id': data.get('res_id', False),
                'res_model': data.get('res_model', False),
                'columns': [data.get('reference_id', False),
                            # data.get('source_doc_name', False),
                            data.get('work_center', False),
                            data.get('discrepancy_message_start', False),
                            data.get('discrepancy_message_end', False)],
                'level': 1,
                'unfoldable': True
            })

        _logger.info("return _list_to_lines")
        return lines

    @api.model
    def _list_to_quantity_lines(self, discrepancy_list_data):
        lines = []
        _logger.info("in _list_to_lines")
        for data in discrepancy_list_data:
            lines.append({
                'id': autoIncrement(),
                'model': data['res_model'],
                'model_id': data['res_id'],
                'source_doc_name': data['source_doc_name'],
                'work_center': data.get('work_center', False),
                'product_name': data.get('product_name', False),
                'is_used': True,
                'discrepancy_message': data.get('discrepancy_message', False),
                'discrepancy_status': data.get('discrepancy_status', False),
                'reference': data.get('reference_id', False),
                'res_id': data.get('res_id', False),
                'res_model': data.get('res_model', False),
                'columns': [data.get('reference_id', False),
                            # data.get('source_doc_name', False),
                            data.get('work_center', False),
                            data.get('product_name', False),
                            data.get('discrepancy_message', False)],
                'level': 1,
                'unfoldable': True
            })

        _logger.info("return _list_to_lines")
        return lines

    @api.model
    def _recursive_node(self, parent_node, discrepancy_list_data):
        _logger.info("into recursive node")
        current_date = datetime.now()
        current_date_str = datetime.strftime(current_date, "%Y-%m-%d %H:%M:%S")
        current_date_frmt = datetime.strptime(current_date_str, "%Y-%m-%d %H:%M:%S")
        _logger.info(current_date_frmt)
        mo_line = self._get_production_data(parent_node, current_date_frmt)
        discrepancy_list_data.append(mo_line)
        res_id = parent_node.res_id
        _logger.info(res_id)
        work_order_data = self.env['mrp.workorder'].search([('production_id', '=', res_id)])
        _logger.info("work_order_data")
        _logger.info(work_order_data)
        if work_order_data:
            for work_order in work_order_data:
                wo_line = self._get_wo_data(parent_node, work_order, current_date_frmt)
                discrepancy_list_data.append(wo_line)
        nodes = parent_node.child_ids;
        _logger.info("check second node")
        _logger.info(nodes)
        if nodes:
            for node in nodes:
                node_id = node.id
                _logger.info(node_id)
                res_model = node.res_model
                if res_model == "mrp.production":
                    discrepancy_list_data = self._recursive_node(node, discrepancy_list_data)
                if res_model == "purchase.order":
                    po_line = self._get_purchase_data(node, current_date_frmt, parent_node)
                    discrepancy_list_data.append(po_line)
                if res_model == "purchase.order.line":
                    po_line = self._get_purchase_line_data(node, current_date_frmt, parent_node)
                    discrepancy_list_data.append(po_line)
        return discrepancy_list_data

    @api.model
    def _get_production_data(self, node, current_date_frmt):
        list_data = {}
        res_model = node.res_model
        _logger.info(res_model)
        res_id = node.res_id
        _logger.info(res_id)
        production_data = self.env[res_model].search([('id', '=', res_id)])
        discrepancy_message_start = "Scheduled start time not reached"
        discrepancy_message_end = "Scheduled finish time not reached"
        discrepancy_start_status = False
        discrepancy_finish_status = False
        if current_date_frmt >= production_data.date_planned_start and ((production_data.state == "planned" or production_data.state == "confirmed") and production_data.state != "cancel"):
            discrepancy_message_start = production_data.name + " Missed scheduled start time of " + str(
                production_data.date_planned_start) + " date"
            discrepancy_start_status = True
        if current_date_frmt >= production_data.date_planned_finished and (
                production_data.state != "done" and production_data.state != "cancel"):
            discrepancy_message_end = production_data.name + " Missed scheduled finish time of " + str(
                production_data.date_planned_finished) + " date"
            discrepancy_finish_status = True
        if production_data.state == "cancel":
            discrepancy_message_start = "Canceled"
            discrepancy_message_end = "Canceled"

        name = production_data.name
        ref = self._get_reference(res_model, res_id, name)
        list_data = {
            "res_model": res_model,
            "res_id": res_id,
            "source_doc_name": name,
            "work_center": "",
            "discrepancy_message_start": discrepancy_message_start,
            "discrepancy_message_end": discrepancy_message_end,
            "discrepancy_start_status": discrepancy_start_status,
            "discrepancy_finish_status": discrepancy_finish_status,
            "reference_id": ref
        }
        _logger.info(list_data)
        return list_data

    @api.model
    def _get_purchase_data(self, node, current_date_frmt, parent_node):
        res_model = node.res_model
        _logger.info(res_model)
        res_id = node.res_id
        _logger.info(res_id)

        production_data = self.env[parent_node.res_model].search([('id', '=', parent_node.res_id)])
        purchase_data = self.env[res_model].search([('id', '=', res_id)])

        discrepancy_message_start = "Scheduled start time not reached"
        discrepancy_message_end = "Scheduled finish time not reached"
        discrepancy_start_status = False
        discrepancy_finish_status = False

        name = production_data.name + " - " + purchase_data.name
        ref = self._get_reference(res_model, res_id, name)

        current_date_frmt = current_date_frmt.date()
        if current_date_frmt > purchase_data.date_approve or purchase_data.state == "purchase":
            discrepancy_message_start = "Purchase done"
            discrepancy_message_end = ""
        else:
            discrepancy_message_start = "Purchase order is still pending."
            discrepancy_message_end = "Purchase order is still pending."
            discrepancy_start_status = True
            discrepancy_finish_status = True
        # _logger.info(ref)
        list_data = {
            "res_model": res_model,
            "res_id": res_id,
            "source_doc_name": name,
            "work_center": "",
            "discrepancy_message_start": discrepancy_message_start,
            "discrepancy_message_end": discrepancy_message_end,
            "discrepancy_start_status": discrepancy_start_status,
            "discrepancy_finish_status": discrepancy_finish_status,
            "reference_id": ref
        }
        return list_data

    @api.model
    def _get_purchase_line_data(self, node, current_date_frmt, parent_node):
        res_model = node.res_model
        _logger.info(res_model)
        res_id = node.res_id
        _logger.info(res_id)

        production_data = self.env[parent_node.res_model].search([('id', '=', parent_node.res_id)])
        purchase_data = self.env[res_model].search([('id', '=', res_id)])

        discrepancy_message_start = "Scheduled start time not reached"
        discrepancy_message_end = "Scheduled finish time not reached"
        discrepancy_start_status = False
        discrepancy_finish_status = False

        name = production_data.name + " - " + purchase_data.order_id.name
        ref = self._get_reference(res_model, res_id, name)

        # current_date_frmt = current_date_frmt.date()
        if current_date_frmt >= production_data.date_planned_start and purchase_data.product_qty > purchase_data.qty_received:
            discrepancy_message_start = "Purchase order missed parent MO's scheduled start date"
            discrepancy_message_end = ""
            discrepancy_start_status = True
            discrepancy_finish_status = True
        else:
            discrepancy_message_start = "No Discrepancy"
            discrepancy_message_end = ""
        # _logger.info(ref)
        list_data = {
            "res_model": res_model,
            "res_id": res_id,
            "source_doc_name": name,
            "work_center": "",
            "discrepancy_message_start": discrepancy_message_start,
            "discrepancy_message_end": discrepancy_message_end,
            "discrepancy_start_status": discrepancy_start_status,
            "discrepancy_finish_status": discrepancy_finish_status,
            "reference_id": ref
        }
        return list_data

    @api.model
    def _get_wo_data(self, node, work_order, current_date_frmt):
        list_data = {}
        res_model = node.res_model
        _logger.info(res_model)
        res_id = node.res_id
        _logger.info(res_id)
        production_data = self.env[res_model].search([('id', '=', res_id)])
        discrepancy_message_start = "Scheduled start time not reached"
        discrepancy_message_end = "Scheduled finish time not reached"
        discrepancy_start_status = False
        discrepancy_finish_status = False
        if current_date_frmt >= work_order.date_planned_start and (
                (work_order.state == "ready" or work_order.state == "pending") and work_order.state != "cancel"):
            discrepancy_message_start = work_order.name + " Missed scheduled start time of " + str(
                work_order.date_planned_start) + " date"
            discrepancy_start_status = True
        if current_date_frmt >= work_order.date_planned_finished and (
                work_order.state != "done" and work_order.state != "cancel"):
            discrepancy_message_end = work_order.name + " Missed scheduled finish time of " + str(
                work_order.date_planned_finished) + " date"
            discrepancy_finish_status = True
        if work_order.state == "cancel":
            discrepancy_message_start = "Canceled"
            discrepancy_message_end = "Canceled"

        name = production_data.name + " - " + work_order.name
        ref = self._get_reference('mrp.workorder', work_order.id, name)
        list_data = {
            "res_model": 'mrp.workorder',
            "res_id": work_order.id,
            "source_doc_name": name,
            "work_center": work_order.workcenter_id.name,
            "discrepancy_message_start": discrepancy_message_start,
            "discrepancy_message_end": discrepancy_message_end,
            "discrepancy_start_status": discrepancy_start_status,
            "discrepancy_finish_status": discrepancy_finish_status,
            "reference_id": ref
        }
        return list_data

    @api.model
    def _quantity_recursive_node(self, parent_node, discrepancy_list_data):
        _logger.info("into recursive node")
        current_date = datetime.now()
        current_date_str = datetime.strftime(current_date, "%Y-%m-%d %H:%M:%S")
        current_date_frmt = datetime.strptime(current_date_str, "%Y-%m-%d %H:%M:%S")
        _logger.info(current_date_frmt)
        # mo_line = self._get_production_data(parent_node, current_date_frmt)
        # discrepancy_list_data.append(mo_line)
        res_id = parent_node.res_id
        _logger.info(res_id)
        work_order_data = self.env['mrp.workorder'].search([('production_id', '=', res_id)])
        _logger.info("work_order_data")
        _logger.info(work_order_data)
        if work_order_data:
            for work_order in work_order_data:
                wo_line = self._get_wo_quantity_data(parent_node, work_order, current_date_frmt)
                discrepancy_list_data.append(wo_line)
        nodes = parent_node.child_ids;
        _logger.info("check second node")
        _logger.info(nodes)
        if nodes:
            for node in nodes:
                node_id = node.id
                _logger.info(node_id)
                res_model = node.res_model
                _logger.info(res_model)
                if res_model == "mrp.production":
                    discrepancy_list_data = self._quantity_recursive_node(node, discrepancy_list_data)
                if res_model == "purchase.order":
                    po_line = self._get_purchase_quantity_data(node, current_date_frmt, parent_node)
                    discrepancy_list_data.extend(po_line)
                if res_model == "purchase.order.line":
                    po_line = self._get_purchase_line_quantity_data(node, current_date_frmt, parent_node)
                    discrepancy_list_data.append(po_line)
        return discrepancy_list_data

    @api.model
    def _get_wo_quantity_data(self, node, work_order, current_date_frmt):
        list_data = {}
        res_model = node.res_model
        _logger.info(res_model)
        res_id = node.res_id
        _logger.info(res_id)
        production_data = self.env[res_model].search([('id', '=', res_id)])
        discrepancy_message = "No discrepancy"
        discrepancy_status = False
        product_name = work_order.product_id.name
        if current_date_frmt >= work_order.date_planned_finished and work_order.state != "cancel" and work_order.qty_produced < work_order.qty_producing:
            discrepancy_message = work_order.name + " failed to produce required quantity. Current status " + str(work_order.qty_produced) + " / " + str(work_order.qty_producing)
            discrepancy_status = True
        if current_date_frmt >= work_order.date_planned_finished and work_order.state != "cancel" and work_order.qty_produced > work_order.qty_producing:
            discrepancy_message = work_order.name + " produced extra than required quantity. Current status " + str(work_order.qty_produced) + " / " + str(work_order.qty_producing)
            discrepancy_status = True
        if work_order.state == "cancel":
            discrepancy_message = "Canceled"
            discrepancy_message = "Canceled"

        name = production_data.name + " - " + work_order.name
        ref = self._get_reference('mrp.workorder', work_order.id, name)
        list_data = {
            "res_model": 'mrp.workorder',
            "res_id": work_order.id,
            "source_doc_name": name,
            "work_center": work_order.workcenter_id.name,
            "product_name": product_name,
            "discrepancy_message": discrepancy_message,
            "discrepancy_status": discrepancy_status,
            "reference_id": ref
        }
        return list_data

    @api.model
    def _get_purchase_quantity_data(self, node, current_date_frmt, parent_node):
        pq_list = []
        res_model = node.res_model
        _logger.info(res_model)
        res_id = node.res_id
        _logger.info(res_id)
        bom_plist = []

        production_data = self.env[parent_node.res_model].search([('id', '=', parent_node.res_id)])
        bom_line_data = self.env['mrp.bom.line'].search([('bom_id', '=', production_data.bom_id.id)])

        for bom_line in bom_line_data:
            bom_plist.append(bom_line.product_id)

        purchase_data = self.env[res_model].search([('id', '=', res_id)])
        purchase_order_line = self.env['purchase.order.line'].search([('order_id', '=', res_id)])
        discrepancy_message = "No discrepancy"
        discrepancy_status = False
        name = "";
        ref = "";

        i = 0
        for line in purchase_order_line:
            if line.product_id in bom_plist:
                name = "";
                ref = "";
                i = i + 1
                if i == 1:
                    name = production_data.name + " - " + purchase_data.name
                    ref = self._get_reference(res_model, res_id, name)
                if current_date_frmt >= production_data.date_planned_start and line.product_qty > line.qty_received:
                    discrepancy_message = purchase_data.name + " - " + line.name + " failed to receive required quantity. Current status " + str(
                        line.qty_received) + " / " + str(line.product_qty)
                    discrepancy_status = True
                if current_date_frmt >= production_data.date_planned_start and line.product_qty < line.qty_received:
                    discrepancy_message = purchase_data.name + " - " + line.name + " received extra quantity. Current status " + str(
                        line.qty_received) + " / " + str(line.product_qty)
                    discrepancy_status = True
                list_data = {
                    "res_model": res_model,
                    "res_id": res_id,
                    "source_doc_name": name,
                    "work_center": "",
                    "product_name": line.name,
                    "discrepancy_message": discrepancy_message,
                    "discrepancy_status": discrepancy_status,
                    "reference_id": ref
                }
                pq_list.append(list_data)

        return pq_list

    @api.model
    def _get_purchase_line_quantity_data(self, node, current_date_frmt, parent_node):

        res_model = node.res_model
        _logger.info(res_model)
        res_id = node.res_id
        _logger.info(res_id)

        production_data = self.env[parent_node.res_model].search([('id', '=', parent_node.res_id)])
        purchase_data = self.env[res_model].search([('id', '=', res_id)])

        discrepancy_message = "No Discrepancy"
        discrepancy_status = False

        name = production_data.name + " - " + purchase_data.order_id.name
        ref = self._get_reference(res_model, res_id, name)

        # current_date_frmt = current_date_frmt.date()
        if current_date_frmt >= production_data.date_planned_start and purchase_data.product_qty > purchase_data.qty_received:
            discrepancy_message = purchase_data.order_id.name + " - " + purchase_data.name + " failed to receive required quantity. Current status " + str(
                purchase_data.qty_received) + " / " + str(purchase_data.product_qty)
            discrepancy_status = True
        if current_date_frmt >= production_data.date_planned_start and purchase_data.product_qty < purchase_data.qty_received:
            discrepancy_message = purchase_data.order_id.name + " - " + purchase_data.name + " received extra quantity. Current status " + str(
                purchase_data.qty_received) + " / " + str(purchase_data.product_qty)
            discrepancy_status = True
        # _logger.info(ref)
        list_data = {
            "res_model": res_model,
            "res_id": res_id,
            "source_doc_name": name,
            "work_center": "",
            "product_name": purchase_data.name,
            "discrepancy_message": discrepancy_message,
            "discrepancy_status": discrepancy_status,
            "reference_id": ref
        }
        _logger.info(list_data)
        return list_data

    @api.model
    def _get_reference(self, res_model, res_id, name):
        res_model = res_model
        res_id = res_id
        ref = name
        return ref


